#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Handy


class AbstractDialog:
    def __init__(self, mainWindow, uiTemplatePath, uiDialogId) -> None:
        self.mainWindow = mainWindow
        self.window = None

        self.builderTemplatePath = uiTemplatePath
        self.builderObjectId = uiDialogId

    def initWindow(self, builder, window) -> None:
        pass

    def __initWindow(self) -> None:
        builder = Gtk.Builder()
        builder.add_from_file(self.builderTemplatePath)

        self.window = builder.get_object(self.builderObjectId)
        self.window.connect("destroy", self._destroyWindow)
        self.window.set_transient_for(self.mainWindow.window)
        self.window.set_modal(True)

        self.initWindow(builder, self.window)

    def _destroyWindow(self, window: Gtk.Widget) -> None:
        self.window = None

        if not self.mainWindow.isVisible():
            self.mainWindow.exit()

    def show(self) -> None:
        if self.window is None:
            self.__initWindow()

        self.window.show()

    def hide(self) -> None:
        if self.window is None:
            return

        self.window.hide()

    def isVisible(self) -> bool:
        if self.window is None:
            return False

        return self.window.get_property("visible")
