#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Any, Iterable

from gi.repository import GdkPixbuf, GObject

from manuskript.data.labels import Label, LabelHost
from manuskript.ui.util import pixbufFromColor
from manuskript.ui.picker.abstractGridPicker import AbstractGridPicker


class LabelPicker(AbstractGridPicker):
    __gsignals__ = {"label-selected": (GObject.SignalFlags.RUN_FIRST, None, (object,))}

    def __init__(self, labels: LabelHost) -> None:
        self.labels: LabelHost = labels

        AbstractGridPicker.__init__(self, enableSearch=True, columns=3)

        self.connect("item-selected", self._labelItemSelected)

    def show(self) -> None:
        AbstractGridPicker.show(self)

    def shouldIncludeItem(self, item: Any) -> bool:
        return type(item) is Label

    def getItems(self) -> Iterable[Any]:
        return self.labels

    def getItemLabel(self, item: Any) -> str:
        if type(item) is Label:
            return item.name
        else:
            return ""

    def getItemPixbuf(self, item: Any) -> GdkPixbuf:
        if type(item) is Label:
            return pixbufFromColor(item.color)
        else:
            return None

    def getItemFilterKey(self, item: Any) -> Any:
        return None

    def _labelItemSelected(self, picker: AbstractGridPicker, item: Any) -> None:
        if type(item) is Label:
            picker.emit("label-selected", item)
