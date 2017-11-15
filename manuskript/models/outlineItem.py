#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.models.abstractItem import abstractItem


class outlineItem(abstractItem):
    def __init__(self, model=None, title="", _type="folder", xml=None, parent=None, ID=None):
        abstractItem.__init__(self, model, title, _type, xml, parent, ID)
