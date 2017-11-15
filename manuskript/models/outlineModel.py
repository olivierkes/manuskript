#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.models.abstractModel import abstractModel


class outlineModel(abstractModel):
    def __init__(self, parent):
        abstractModel.__init__(self, parent)

    def findItemsByPOV(self, POV):
        "Returns a list of IDs of all items whose POV is ``POV``."
        return self.rootItem.findItemsByPOV(POV)
