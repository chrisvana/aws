# Copyright 2014
# Author: Christopher Van Arsdale

import boto
import boto.sqs
from aws.setup.base import BaseClient

class QueueClient(BaseClient):
    def __init__(self, name, region):
        self.queue_name = name
        self.queue = None
        self.sqs_conn = boto.sqs.connect_to_region(region)

    def GetItem(self):
        return self.queue

    def SetItem(self, item):
        self.queue = item

    def existing(self):
        return self.sqs_conn.get_queue(self.queue_name)

    def SetupNew(self):
        print 'Creating queue: %s ' % self.queue_name
        self.queue = self.sqs_conn.create_queue(self.queue_name, 120)

    def DeleteItem(self, item):
        self.sqs_conn.delete_queue(item)

class QueueSet:
    def __init__(self, instance, region):
        self.instance = instance
        self.input_queue = QueueClient('%s-input' % instance, region)
        self.error_queue = QueueClient('%s-error' % instance, region)
        self.output_queue = QueueClient('%s-output' % instance, region)

    def TearDown(self):
        self.input_queue.TearDown()
        self.error_queue.TearDown()
        self.output_queue.TearDown()

    def Initialized(self):
        return (self.input_queue.Initialized() and
                self.error_queue.Initialized() and
                self.output_queue.Initialized())

    def SetupExisting(self):
        self.input_queue.SetupExisting()
        self.error_queue.SetupExisting()
        self.output_queue.SetupExisting()

    def FindOrNew(self):
        self.output_queue.FindOrNew()
        self.error_queue.FindOrNew()
        self.input_queue.FindOrNew()
        self.input_queue.queue.set_attribute(
            'RedrivePolicy',
            '{"maxReceiveCount":"5", "deadLetterTargetArn":"%s"}' %
            self.error_queue.queue.arn)
