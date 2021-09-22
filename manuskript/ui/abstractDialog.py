#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Handy", "1")

from gi.repository import Gtk, Handy

Handy.init()


class AbstractDialog:

    def __init__(self, mainWindow, uiTemplatePath, uiDialogId):
        self.mainWindow = mainWindow
        self.window = None

        self.builderTemplatePath = uiTemplatePath
        self.builderObjectId = uiDialogId

    def initWindow(self, builder, window):
        pass

    def __initWindow(self):
        builder = Gtk.Builder()
        builder.add_from_file(self.builderTemplatePath)

        self.window = builder.get_object(self.builderObjectId)
        self.window.connect("destroy", self.__destroyWindow)
        self.window.set_transient_for(self.mainWindow.window)
        self.window.set_modal(True)

        self.initWindow(builder, self.window)

    def __destroyWindow(self, window: Gtk.Widget):
        self.window = None

    def show(self):
        if self.window is None:
            self.__initWindow()

        self.window.show_all()

    def hide(self):
        if self.window is None:
            return

        self.window.hide()
