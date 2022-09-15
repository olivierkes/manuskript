#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Handy

from manuskript.data import Template, TemplateLevel, TemplateKind
from manuskript.util import validInt, validString

from manuskript.ui.abstractDialog import AbstractDialog
from manuskript.ui.util import bindMenuItem


class StartupWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/startup.glade", "startup_window")

        self.templates = Template.getDefaultTemplates()

        self.headerBar = None
        self.templatesLeaflet = None

        self.templatesStore = None
        self.fictionTemplatesStore = None
        self.nonfictionTemplatesStore = None
        self.demoTemplatesStore = None

        self.templateSelections = list()

    def initWindow(self, builder, window):
        self.headerBar = builder.get_object("header_bar")
        self.templatesLeaflet = builder.get_object("templates_leaflet")

        self.templatesLeaflet.bind_property("folded", self.headerBar, "show-close-button",
                                            GObject.BindingFlags.SYNC_CREATE |
                                            GObject.BindingFlags.INVERT_BOOLEAN)

        bindMenuItem(builder, "open_menu_item", self.mainWindow.openAction)
        bindMenuItem(builder, "quit_menu_item", self.mainWindow.quitAction)

        self.templatesStore = builder.get_object("templates_store")

        for index in range(len(self.templates)):
            tree_iter = self.templatesStore.append()

            if tree_iter is None:
                continue

            template = self.templates[index]

            self.templatesStore.set_value(tree_iter, 0, validInt(index))
            self.templatesStore.set_value(tree_iter, 1, validString(template.name))
            self.templatesStore.set_value(tree_iter, 2, TemplateKind.asValue(template.kind))

        self.fictionTemplatesStore = builder.get_object("fiction_templates_store")
        self.nonfictionTemplatesStore = builder.get_object("nonfiction_templates_store")
        self.demoTemplatesStore = builder.get_object("demo_templates_store")

        self.fictionTemplatesStore.set_visible_func(
            lambda model, iter, userdata: model[iter][2] == TemplateKind.FICTION.value)
        self.nonfictionTemplatesStore.set_visible_func(
            lambda model, iter, userdata: model[iter][2] == TemplateKind.NONFICTION.value)
        self.demoTemplatesStore.set_visible_func(
            lambda model, iter, userdata: model[iter][2] == TemplateKind.DEMO.value)

        self.fictionTemplatesStore.refilter()
        self.nonfictionTemplatesStore.refilter()
        self.demoTemplatesStore.refilter()

        self.templateSelections = [
            builder.get_object("fiction_template_selection"),
            builder.get_object("nonfiction_template_selection"),
            builder.get_object("demo_template_selection")
        ]

        for selection in self.templateSelections:
            selection.connect("changed", self.templateSelectionChanged)

    def templateSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            return

        for other in self.templateSelections:
            if other != selection:
                other.unselect_all()

        index = model[tree_iter][0]
        template = self.templates[index]

        print(template.name)