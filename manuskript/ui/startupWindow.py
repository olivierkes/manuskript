#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Handy

from manuskript.data import Template, TemplateLevel, TemplateKind
from manuskript.util import validInt, validString

from manuskript.ui.abstractDialog import AbstractDialog
from manuskript.ui.startup import TemplateEntry
from manuskript.ui.util import bindMenuItem


class StartupWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/startup.glade", "startup_window")

        self.templates = Template.getDefaultTemplates()
        self.template = None

        self.headerBar = None
        self.templatesLeaflet = None

        self.templatesStore = None
        self.fictionTemplatesStore = None
        self.nonfictionTemplatesStore = None
        self.demoTemplatesStore = None

        self.templateSelections = list()
        self.templateLevelsListbox = None

        self.goalLabel = None
        self.addLevelButton = None
        self.addGoalButton = None

    def initWindow(self, builder, window):
        self.headerBar = builder.get_object("header_bar")
        self.templatesLeaflet = builder.get_object("templates_leaflet")

        self.templatesLeaflet.bind_property("folded", self.headerBar, "show-close-button",
                                            GObject.BindingFlags.SYNC_CREATE |
                                            GObject.BindingFlags.INVERT_BOOLEAN)

        bindMenuItem(builder, "open_menu_item", self.mainWindow.openAction)
        bindMenuItem(builder, "quit_menu_item", self.mainWindow.quitAction)

        bindMenuItem(builder, "about_menu_item", self.mainWindow.aboutAction)

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

        self.templateLevelsListbox = builder.get_object("template_levels_listbox")

        self.goalLabel = builder.get_object("goal_label")
        self.addLevelButton = builder.get_object("add_level_button")
        self.addGoalButton = builder.get_object("add_goal_button")

        self.addLevelButton.connect("clicked", self.addLevelClicked)
        self.addGoalButton.connect("clicked", self.addGoalClicked)

    def loadTemplate(self, template: Template):
        self.template = template
        self.templateLevelsListbox.foreach(lambda child: self.templateLevelsListbox.remove(child))

        self.addLevelButton.set_sensitive(self.template is not None)
        self.addGoalButton.set_sensitive((self.template is not None) and (self.template.goal is None))

        if self.template is None:
            return

        for level in self.template.levels:
            entry = TemplateEntry(self)
            entry.bindTemplate(self.template, level)

            self.templateLevelsListbox.add(entry.widget)
            entry.show()

        if self.template.goal is not None:
            entry = TemplateEntry(self)
            entry.bindTemplate(self.template)

            self.templateLevelsListbox.add(entry.widget)
            entry.show()

        self.goalLabel.set_text(self.template.getGoalString())

    def templateSelectionChanged(self, selection: Gtk.TreeSelection):
        model, tree_iter = selection.get_selected()

        if tree_iter is None:
            return

        for other in self.templateSelections:
            if other != selection:
                other.unselect_all()

        index = model[tree_iter][0]

        self.loadTemplate(self.templates[index] if (index >= 0) and (index < len(self.templates)) else None)

    def addLevelClicked(self, button: Gtk.Button):
        if self.template is None:
            return

        self.template.addLevel()
        self.loadTemplate(self.template)

    def addGoalClicked(self, button: Gtk.Button):
        if self.template is None:
            return

        self.template.addGoal()
        self.loadTemplate(self.template)
