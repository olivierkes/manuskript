#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Handy

Handy.init()

from manuskript.data import Settings


class ViewsPage:

    def __init__(self, settings: Settings):
        self.settings = settings

        builder = Gtk.Builder()
        builder.add_from_file("ui/settings/views.glade")

        self.widget = builder.get_object("views_page")
