# Copyright 2014
# Author: Christopher Van Arsdale

import boto
import aws.config.workqueue
from aws.setup.queue import QueueSet
from aws.setup.autoscale import AutoScaleClient
from aws.setup.alarm import AlarmSet
import aws.setup.spot

class SetupClient:
    def __init__(self, config):
        self.config = config
        if not self.config.IsValid():
            raise 'Invalid config.'
        self.sqs = QueueSet(config.Instance(), config.Region())
        self.ec2_conn = boto.ec2.connect_to_region(region_name=config.Region())
        self.price_history = aws.setup.spot.GetPriceInfo(self.ec2_conn)
        chosen = None
        for p in self.price_history:
            if config.spot.IsOkArchPrice(p.arch, p.last):
                chosen = p
                break
        if chosen is None:
            raise 'Could not find good architecture fit.'
        else:
            config.spot.instance_type = chosen.arch
        self.scale = AutoScaleClient(config.Instance(), config, [chosen.zone])
        self.alarms = None

    def TearDown(self):
        if self.alarms is None and not self.scale.Initialized():
            self.scale.SetupExisting()
        self.CreateAlarmTemplate()

        self.scale.TearDown()
        self.alarms.TearDown()
        self.sqs.TearDown()

    def CreateExisting(self):
        if self.sqs is None:
            self.sqs.SetupExisting()
        if self.scale is None:
            self.scale.SetupExisting()
        self.CreateAlarmTemplate()
        self.alarms.SetupExisting()

    def CreateAlarmTemplate(self):
        if self.alarms is None:
            self.alarms = AlarmSet(instance = self.config.Instance(),
                                   region = self.config.Region(),
                                   input_queue_name = self.sqs.input_queue.queue_name,
                                   scale_arn_up = self.scale.ScaleUpARN(),
                                   scale_arn_down = self.scale.ScaleDownARN())

    def FindOrNew(self):
        self.sqs.FindOrNew()
        self.scale.FindOrNew()
        self.CreateAlarmTemplate()
        self.alarms.FindOrNew()

