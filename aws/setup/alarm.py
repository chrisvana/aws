# Copyright 2014
# Author: Christopher Van Arsdale

import boto
import boto.ec2.cloudwatch
from boto.ec2.cloudwatch import MetricAlarm
from aws.setup.base import BaseClient

class AlarmClient(BaseClient):
    def __init__(self, region, alarm_template):
        self.alarm = None
        self.alarm_template = alarm_template
        self.alarm_conn = boto.ec2.cloudwatch.connect_to_region(region)

    def GetItem(self):
        return self.alarm

    def SetItem(self, item):
        self.alarm = item

    def existing(self):
        l = self.alarm_conn.describe_alarms(alarm_names=[self.alarm_template.name])
        if len(l) > 0:
            return l[0]
        return None

    def SetupNew(self):
        self.alarm = self.alarm_conn.create_alarm(self.alarm_template)

    def DeleteItem(self, item):
        print 'Deleting alarm: %s' % self.alarm_template.name
        self.alarm_conn.delete_alarms([item])

class QueueLengthAlarm:
    def __init__(self, prefix=None, period=60, evaluation_periods=2):
        self.prefix = prefix
        self.period = period
        self.evaluation_periods = evaluation_periods

    def GetUpMetric(self, queue_name, arn):
        return MetricAlarm(
            name='%sscale_up_sqs' % self.prefix,
            namespace='AWS/SQS',
            metric='ApproximateNumberOfMessagesVisible',
            statistic='Sum',
            comparison='>',
            threshold='1',
            period=self.period,
            evaluation_periods=self.evaluation_periods,
            alarm_actions=[arn],
            dimensions={"QueueName": queue_name})

    def GetDownMetric(self, queue_name, arn):
        return MetricAlarm(
            name='%sscale_down_sqs' % self.prefix,
            namespace='AWS/SQS',
            metric='NumberOfEmptyReceives',
            statistic='Sum',
            comparison='>',
            threshold='1',
            period=self.period,
            evaluation_periods=self.evaluation_periods,
            alarm_actions=[arn],
            dimensions={"QueueName": queue_name})

class AlarmSet:
    def __init__(self, instance, region, input_queue_name,
                 scale_arn_up, scale_arn_down):
        base = QueueLengthAlarm(instance + "-alarm-")
        self.scale_up_policy = AlarmClient(
            region, base.GetUpMetric(input_queue_name, scale_arn_up))
        self.scale_down_policy = AlarmClient(
            region, base.GetDownMetric(input_queue_name, scale_arn_down))

    def SetupExisting(self):
        self.scale_up_policy.SetupExisting()
        self.scale_down_policy.SetupExisting()

    def TearDown(self):
        self.scale_up_policy.TearDown()
        self.scale_down_policy.TearDown()

    def FindOrNew(self):
        self.scale_up_policy.FindOrNew()
        self.scale_down_policy.FindOrNew()
