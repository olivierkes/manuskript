#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk


class AbstractView:
    def __init__(self) -> None:
        self.widget = None
        self.active = False

    def activate(self) -> None:
        self.active = True

    def deactivate(self) -> None:
        self.active = False

    def show(self) -> None:
        if not self.widget:
            return

        self.widget.show_all()
