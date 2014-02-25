# Copyright 2014
# Author: Christopher Van Arsdale

class BootstrapConfig:
    def __init__(self):
        self.script = ''

    def LoadFromString(self, script=''):
        self.script = script

    def LoadFromFile(self, filename):
        self.script = open(filename).read()

    def getBoostrapScript(self):
        return self.script

    def IsValid(self):
        return True
