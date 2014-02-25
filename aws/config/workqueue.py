# Copyright 2014
# Author: Christopher Van Arsdale

import json

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

    def LoadFromJsonString(self, json_val):
        parsed = jsons.loads(json_val)
        max_expense = float(parsed['max_expense'])
        self.instance = parsed['instance']
        if parsed['spot'] is not None:
            spot.LoadFromJsonString(json.dumps(parsed['spot']))
        if parsed['bootstrap'] is not None:
            bootstrap.LoadFromString(parsed['bootstrap'])
