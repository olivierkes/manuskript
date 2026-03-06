#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk


class AbstractView:

    def __init__(self):
        self.widget = None
        self.active = False
    
    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def show(self):
        if not self.widget:
            return

        self.widget.show_all()
