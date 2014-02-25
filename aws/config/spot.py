# Copyright 2014
# Author: Christopher Van Arsdale

import json

class SpotConfig:
    def __init__(self):
        self.bid_price = 0.0
        self.max_nodes = 0
        self.region = 'us-east-1'

    def LoadFromJsonString(self, json_str=''):
        parsed = json.loads(json_str)
        self.bid_price = float(parsed['bid_price'])
        self.max_nodes = int(parsed['max_nodes'])
        self.region = parsed['region']
        if self.region is None or len(region) == 0:
            self.region = 'us-east-1'

    def LoadFromFile(self, filename):
        self.LoadFromJsonString(open(filename).read())

    def IsValid(self):
        return self.bid_price > 0.0 and self.max_nodes > 0 and len(self.region) > 0
        
