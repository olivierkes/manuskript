#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from gi.repository import Gtk
from collections.abc import Iterable

class WidgetGroupItem:
    widget: Gtk.Widget
    associatedvalue: any
    
    def __init__(self, widget: Gtk.Widget, associatedvalue: any):
        self.widget = widget
        self.associatedvalue = associatedvalue

class WidgetGroup:
    items: list[WidgetGroupItem]

    def __init__(self):
        self.items=[]

    def addItem(self, widgetGroupItem: WidgetGroupItem):
        self.items.append(widgetGroupItem)

    def setActiveFromSelection(self, selection: str | list):
        if isinstance(selection, Iterable) and not isinstance(selection, (str, bytes)):
            values = set(selection)
        else:
            values = {selection}

        for item in self.items:
            radioWidget = item.widget
            radioSettingsValue = item.associatedvalue

            if radioSettingsValue in values:
                radioWidget.set_active(True)

    def connect(self, signal: str, callback, *args):
        for item in self.items:
            newArgs = (item.associatedvalue,) + args  
            item.widget.connect(signal, callback, *newArgs)

    def fetchAllActive(self) -> list[any]:
        result=[]
        for item in self.items:
            if item.widget.get_active():
                result.append(item.associatedvalue)
        return result

class WidgetGroupBuilder:
    def __init__(self):
        self.widgetGroup = WidgetGroup()
    
    def addWidget(self, widget: Gtk.Widget, returnedValue: any) -> WidgetGroupBuilder:
        widgetGroupItem=WidgetGroupItem(widget, returnedValue)
        self.widgetGroup.addItem(widgetGroupItem)
        return self
    
    def build(self) -> WidgetGroup:
        return self.widgetGroup
