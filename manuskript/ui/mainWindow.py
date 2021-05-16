#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Handy", "1")

from gi.repository import Gtk, Handy

Handy.init()

from manuskript.ui import GeneralView, SummaryView, CharactersView, PlotView, WorldView, OutlineView, EditorView


class MainWindow:

    @classmethod
    def packViewIntoSlot(cls, builder, id, view_cls):
        slot = builder.get_object(id)

        if slot is None:
            return None

        try:
            view = view_cls()
        except Exception:
            return None

        if view.widget is None:
            return None

        slot.pack_start(view.widget, True, True, 0)
        return view

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("ui/main.glade")

        self.window = builder.get_object("main_window")
        self.window.connect("destroy", Gtk.main_quit)

        self.generalView = MainWindow.packViewIntoSlot(builder, "general_slot", GeneralView)
        self.summaryView = MainWindow.packViewIntoSlot(builder, "summary_slot", SummaryView)
        self.charactersView = MainWindow.packViewIntoSlot(builder, "characters_slot", CharactersView)
        self.plotView = MainWindow.packViewIntoSlot(builder, "plot_slot", PlotView)
        self.worldView = MainWindow.packViewIntoSlot(builder, "world_slot", WorldView)
        self.outlineView = MainWindow.packViewIntoSlot(builder, "outline_slot", OutlineView)
        self.editorView = MainWindow.packViewIntoSlot(builder, "editor_slot", EditorView)

    def show(self):
        self.window.show_all()

    def run(self):
        self.show()
        Gtk.main()
