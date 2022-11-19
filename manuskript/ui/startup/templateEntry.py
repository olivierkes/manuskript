#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from manuskript.data import Template, TemplateLevel
from manuskript.util import validInt, validString


class TemplateEntry:

    def __init__(self, window):
        self.template = None
        self.level = None

        builder = Gtk.Builder()
        builder.add_from_file("ui/startup/template-entry.glade")

        self.window = window
        self.widget = builder.get_object("template_entry")

        self.valueAdjustment = builder.get_object("value_adjustment")
        self.nameBuffer = builder.get_object("name_buffer")

        self.entryStack = builder.get_object("entry_stack")
        self.deleteButton = builder.get_object("delete_button")

        self.deleteButton.connect("clicked", self.deleteClicked)

    def bindTemplate(self, template: Template, level: TemplateLevel = None):
        self.template = template

        if self.template is None:
            self.level = None
            return

        self.level = level if level in self.template.levels else None

        if self.level is None:
            self.valueAdjustment.set_value(0 if self.template.goal is None else validInt(self.template.goal.value))

            self.entryStack.set_visible_child_name("page_label")
        else:
            self.valueAdjustment.set_value(validInt(self.level.size))
            self.nameBuffer.set_text(validString(self.level.name), -1)

            self.entryStack.set_visible_child_name("page_entry")

    def deleteClicked(self, button: Gtk.Button):
        if self.template is None:
            return

        if self.level is None:
            self.template.goal = None
        else:
            self.template.levels.remove(self.level)

        self.window.loadTemplate(self.template)
        self.window = None

        self.template = None
        self.level = None

    def show(self):
        self.widget.show_all()
