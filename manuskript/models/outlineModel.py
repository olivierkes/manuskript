#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.models.abstractModel import abstractModel
from manuskript.models import outlineItem


class outlineModel(abstractModel):
    def __init__(self, parent):
        abstractModel.__init__(self, parent)
        self.rootItem = outlineItem(model=self, title="Root", ID="0")


    def findItemsByPOV(self, POV):
        "Returns a list of IDs of all items whose POV is ``POV``."
        return self.rootItem.findItemsByPOV(POV)
