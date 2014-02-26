# Copyright 2014
# Author: Christopher Van Arsdale

import json
from aws.config.bootstrap import BootstrapConfig
from aws.config.spot import SpotConfig

class WorkqueueConfig:
    def __init__(self):
        self.bootstrap = BootstrapConfig()
        self.spot = SpotConfig()
        self.max_expense = 0.0
        self.instance = ''

    def IsValid(self):
        return (self.max_expense >= 0.0 and
                len(self.instance) > 0 and
                self.bootstrap.IsValid() and
                self.spot.IsValid())

    def Region(self):
        return self.spot.region

    def Instance(self):
        return self.instance

    def LoadFromJsonString(self, json_val):
        parsed = json.loads(json_val)
        max_expense = float(parsed['max_expense'])
        self.instance = parsed['instance']
        if 'spot' in parsed.keys():
            self.spot.LoadFromJsonString(parsed['spot'])
        if 'bootstrap' in parsed.keys():
            self.bootstrap.LoadFromJsonString(parsed['bootstrap'])
