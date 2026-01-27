#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from gi.repository import GObject

from manuskript.data.labels import Label, LabelHost
from manuskript.ui.util import pixbufFromColor
from manuskript.ui.picker.abstractGridPicker import AbstractGridPicker


class LabelPicker(AbstractGridPicker):
    __gsignals__ = {
        "label-selected": (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, labels: LabelHost):
        self.labels: LabelHost = labels

        super().__init__(enableSearch=True, columns=3)

        self.connect("item-selected", self._labelItemSelected)

    def show(self):
        super().show()

    def shouldIncludeItem(self, label: Label):
        return True

    def getItems(self):
        return self.labels

    def getItemLabel(self, label: Label):
        return label.name

    def getItemPixbuf(self, label: Label):
        return pixbufFromColor(label.color)

    def getItemFilterKey(self, label: Label):
        return None

    def _labelItemSelected(self, picker: LabelPicker, label: Label):
        picker.emit("label-selected", label)