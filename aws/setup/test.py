# Copyright 2014
# Author: Christopher Van Arsdale

import boto
import common.base.flags as flags
import sys
# from aws.config.workqueue import WorkqueueConfig
import aws.config.workqueue
from aws.setup.client import SetupClient

FLAGS = flags.FLAGS
flags.d.DEFINE_bool('create', False, 'Create setup.')
flags.d.DEFINE_bool('delete', False, 'Delete setup.')

workqueue_config = """
{
  "instance": "test_initial",
  "max_expense": 1,
  "bootstrap": {
    "script": [
      "#!/bin/bash\\n",
      "sudo apt-get install gcc-4.8 make\\n",
      "echo 'All Done\'\\n"
    ]
  },
  "spot": {
    "bid_price": 0.1,
    "core_bid_price": 0.01,
    "max_nodes": 1,
    "ami": "ami-1d132274",
    "region": "us-east-1"
  }
}
"""


if __name__ == '__main__':
    sys.argv = FLAGS(sys.argv)  # parse flags
    config = aws.config.workqueue.WorkqueueConfig()
    config.LoadFromJsonString(workqueue_config)
    client = SetupClient(config)
    if FLAGS.create:
        client.FindOrNew()
    if FLAGS.delete:
        client.TearDown()
