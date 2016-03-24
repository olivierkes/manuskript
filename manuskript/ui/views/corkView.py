#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QListView

from manuskript import settings
from manuskript.functions import findBackground
from manuskript.ui.views.corkDelegate import corkDelegate
from manuskript.ui.views.dndView import dndView
from manuskript.ui.views.outlineBasics import outlineBasics


class corkView(QListView, dndView, outlineBasics):
    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        dndView.__init__(self, parent)
        outlineBasics.__init__(self, parent)

        self.setResizeMode(QListView.Adjust)
        self.setWrapping(True)
        self.setItemDelegate(corkDelegate())
        self.setSpacing(5)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setFlow(self.LeftToRight)
        self.setSelectionBehavior(self.SelectRows)
        self.updateBackground()

    def updateBackground(self):
        img = findBackground(settings.corkBackground["image"])
        self.setStyleSheet("""QListView {{
            background:{color};
            background-image: url({url});
            }}""".format(
                color=settings.corkBackground["color"],
                url=img
        ))

    def dragMoveEvent(self, event):
        dndView.dragMoveEvent(self, event)
        QListView.dragMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        QListView.mouseReleaseEvent(self, event)
        outlineBasics.mouseReleaseEvent(self, event)
