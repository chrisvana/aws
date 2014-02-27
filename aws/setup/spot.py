# Copyright 2014
# Author: Christopher Van Arsdale

import boto
import boto.ec2
import aws.config
import aws.config.spot

def GetPriceHistory(conn):
    prices = conn.get_spot_price_history(product_description='Linux/UNIX')
    prices = sorted(prices, key=lambda p: p.timestamp)
    by_type = {}
    for f in prices:
        by_type[f.instance_type, f.availability_zone] = []
    for f in prices:
        by_type[f.instance_type, f.availability_zone] += [ f ]
    return by_type

class PriceInfo:
    def __init__(self, arch, zone, last, per_ecore_average, num_cores):
        self.arch = arch
        self.zone = zone
        self.last = last
        self.per_ecore_average = per_ecore_average
        self.num_cores = num_cores

def GetPriceInfo(conn):
    prices = GetPriceHistory(boto.connect_ec2())
    spot = aws.config.spot.SpotCPU()
    price_list = []
    for f in prices.keys():
        price_per_core = spot.GetPerECorePrice(
            f[0],
            sum(p.price for p in prices[f])/len(prices[f]))
        price_list.append(PriceInfo(f[0], f[1], prices[f][0].price,
                                    price_per_core,
                                    spot.GetCpuCount(f[0])))
    price_list = sorted(price_list, key=lambda p: p.per_ecore_average)
    return price_list

