# Copyright 2014
# Author: Christopher Van Arsdale

class SpotConfig:
    def __init__(self):
        self.bid_price = 0.0
        self.max_nodes = 0
        self.min_nodes = 0
        self.region = 'us-east-1'
        self.ami = 'ami-951524fc'
        self.instance_type = 'c1.medium'

    def LoadFromJsonString(self, parsed):
        if 'bid_price' in parsed.keys():
            self.bid_price = float(parsed['bid_price'])
        if 'min_nodes' in parsed.keys():
            self.min_nodes = int(parsed['min_nodes'])
        if 'max_nodes' in parsed.keys():
            self.max_nodes = int(parsed['max_nodes'])
        self.region = parsed['region']
        if self.region is None or len(self.region) == 0:
            self.region = 'us-east-1'

    def LoadFromFile(self, filename):
        self.LoadFromJsonString(open(filename).read())

    def IsValid(self):
        return self.bid_price > 0.0 and self.max_nodes > 0 and len(self.region) > 0
        
