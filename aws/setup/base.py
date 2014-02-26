# Copyright 2014
# Author: Christopher Van Arsdale

class BaseClient(object):
    def HasExisting(self):
        return self.existing() is not None

    def SetupExisting(self):
       self.SetItem(self.existing())

    def FindOrNew(self):
       self.SetupExisting()
       if self.GetItem() is None:
           self.SetupNew()

    def GetItem(self):
        return None

    def SetItem(self, item):
        return

    def ClearItem(self):
        self.SetItem(None)

    def TearDown(self):
        item = self.GetItem()
        if item is None:
            item = self.existing()
        if item is not None:
            self.DeleteItem(item)
        self.ClearItem()

    def Initialized(self):
        return self.GetItem() is not None
