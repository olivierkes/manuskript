#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk

from manuskript.ui.views.abstractView import AbstractView


class SearchView(AbstractView):
    def __init__(self) -> None:
        AbstractView.__init__(self)

        builder = Gtk.Builder()
        builder.add_from_file("ui/search.glade")

        self.widget = builder.get_object("search_view")
