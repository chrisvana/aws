# Copyright 2014
# Author: Christopher Van Arsdale

import boto
from boto.exception import BotoServerError
import boto.ec2.autoscale
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.autoscale import ScalingPolicy
from boto.ec2.tag import Tag
from aws.config.spot import SpotConfig
from aws.setup.base import BaseClient

class LaunchConfig(BaseClient):
    def __init__(self, name, conn, config):
        self.name = name
        self.autoscale_conn = conn
        self.launch_config = None
        self.input_config = config

    def GetItem(self):
        return self.launch_config

    def SetItem(self, item):
        self.launch_config = item

    def existing(self):
        l = self.autoscale_conn.get_all_launch_configurations(names=[self.name])
        if len(l) > 0:
            return l[0]
        return None

    def SetupNew(self):
        lc = LaunchConfiguration(name=self.name,
                                 image_id=self.input_config.spot.ami,
                                 user_data=self.input_config.bootstrap.script,
                                 spot_price=self.input_config.spot.bid_price,
                                 instance_type=self.input_config.spot.instance_type)
        print 'Creating launch config: %s' % self.name
        self.launch_config = self.autoscale_conn.create_launch_configuration(lc)

    def DeleteItem(self, item):
        print 'Deleting launch configuration: %s' % self.name
        item.delete()

class AutoScaleClient(BaseClient):
    def __init__(self, name, config, zones):
        self.input_config = config
        self.name = name + "-auto"
        self.instance = name
        region = config.Region()
        self.autoscale_conn = boto.ec2.autoscale.connect_to_region(region)
        self.ec2_conn = boto.ec2.connect_to_region(region_name=region)
        self.zones = zones
        self.autoscale = None
        self.scale_up_policy = None
        self.scale_down_policy = None
        self.launch_config = LaunchConfig(name + "-lc", self.autoscale_conn, config)

    def GetItem(self):
        return self.autoscale

    def SetItem(self, item):
        self.autoscale = item

    def existing(self):
        l = self.autoscale_conn.get_all_groups([self.name])
        if len(l) > 0:
            return l[0]
        return None

    def SetupNew(self):
        # Launch config first
        ag = AutoScalingGroup(group_name=self.name,
                              availability_zones=self.zones,
                              launch_config=self.launch_config.launch_config,
                              desired_capacity = 0,
                              min_size = self.input_config.spot.min_nodes,
                              max_size = self.input_config.spot.max_nodes,
                              termination_policies = [ 'NewestInstance',
                                                       'ClosestToNextInstanceHour',
                                                       'Default' ],
                              connection=self.autoscale_conn)
        print 'Creating autoscale group: %s' % self.name
        self.autoscale_conn.create_auto_scaling_group(ag)
        self.autoscale = ag

        # Scaling
        self.SetupNewScaling()

        # Tagging
        print 'Adding tag to autoscaling group'
        self.autoscale_conn.create_or_update_tags([
            boto.ec2.autoscale.Tag(key="billing", value=self.instance,
                                   resource_id=ag.name) ])

    def SetupNewScaling(self):
        # Scaling policies
        if self.scale_up_policy is None:
            scale_up_policy = ScalingPolicy(
                name='scale_up', adjustment_type='ChangeInCapacity',
                as_name=self.name, scaling_adjustment=1, cooldown=180)
            print 'Creating scaling policy: %s' % scale_up_policy.name
            self.autoscale_conn.create_scaling_policy(scale_up_policy)

        if self.scale_down_policy is None:
            scale_down_policy = ScalingPolicy(
                name='scale_down', adjustment_type='ChangeInCapacity',
                as_name=self.name, scaling_adjustment=-1, cooldown=180)
            print 'Creating scaling policy: %s' % scale_down_policy.name
            self.autoscale_conn.create_scaling_policy(scale_down_policy)

        # Need ARNs, so re-request:
        self.GetScalePolicies()

    def ScaleUpARN(self):
        return self.scale_up_policy.policy_arn

    def ScaleDownARN(self):
        return self.scale_down_policy.policy_arn

    def GetScalePolicies(self):
        print 'Fetching scaling policy info.'
        try:
            l = self.autoscale_conn.get_all_policies(
                as_group=self.name, policy_names=['scale_up'])
            self.scale_up_policy = None
            if len(l) > 0:
                self.scale_up_policy = l[0]
        except BotoServerError as e:
            self.scale_up_policy = None
            print 'Could not get scale_up_policy: %s' % e

        try:
            l =  self.autoscale_conn.get_all_policies(
                as_group=self.name, policy_names=['scale_down'])
            self.scale_down_policy = None
            if len(l) > 0:
                self.scale_down_policy = l[0]
        except BotoServerError as e:
            self.scale_down_policy = None
            print 'Could not get scale_down_policy: %s' % e

    def SetupExisting(self):
       self.launch_config.SetupExisting()
       super(AutoScaleClient, self).SetupExisting()
       if self.autoscale is not None:
           self.GetScalePolicies()
           self.SetupNewScaling()  # only if they aren't found.
       else:
           self.scale_up_policy = None
           self.scale_down_policy = None

    def FindOrNew(self):
        self.launch_config.FindOrNew()
        super(AutoScaleClient, self).FindOrNew()

    def TearDown(self):
        self.scale_up_policy = None
        self.scale_down_policy = None
        super(AutoScaleClient, self).TearDown()
        self.launch_config.TearDown()  # happens afterwards

    def DeleteItem(self, item):
        print 'Deleting AutoScalingGroup %s' % self.name
        item.shutdown_instances()
        item.delete()

    def Initialized(self):
        return (self.launch_config.Initialized() and
                super(AutoScaleClient, self).Initialized())
