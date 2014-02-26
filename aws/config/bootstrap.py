# Copyright 2014
# Author: Christopher Van Arsdale

import string

class BootstrapConfig:
    def __init__(self):
        self.script = ''

    def LoadFromFile(self, filename):
        self.SetScript(open(filename).read())

    def LoadFromJsonString(self, parsed):
        if 'script' in parsed.keys():
            self.SetScript(string.join(parsed['script']))
        if 'file' in parsed.keys():
            self.LoadFromFile(parsed['file'])

    def SetScript(self, script):
        self.script = script
        assert len(script) == 0 or script.startswith("#!")

    def IsValid(self):
        return True
