#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView


class dndView(QAbstractItemView):
    def __init__(self, parent=None):
        # QAbstractItemView.__init__(self, parent)
        self.setDragDropMode(self.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(self.ExtendedSelection)

    def dragMoveEvent(self, event):
        # return QAbstractItemView.dragMoveEvent(self, event)
        # print(a)
        if event.keyboardModifiers() & Qt.ControlModifier:
            event.setDropAction(Qt.CopyAction)
        else:
            event.setDropAction(Qt.MoveAction)
