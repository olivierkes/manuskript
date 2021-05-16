#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class GeneralView:

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("ui/general.glade")

        self.widget = builder.get_object("general_view")

    def show(self):
        self.widget.show_all()
