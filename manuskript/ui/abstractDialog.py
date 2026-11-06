#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any

from gi.repository import Gtk, Handy


class AbstractDialog:
    def __init__(self, mainWindow: Any, uiTemplatePath: str, uiDialogId: str) -> None:
        self.mainWindow = mainWindow
        self.window: Gtk.Window = None

        self.builderTemplatePath: str = uiTemplatePath
        self.builderObjectId: str = uiDialogId

    def initWindow(self, builder: Gtk.Builder, window: Any) -> None:
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

        if self.window is None:
            return

        self.window.show()

    def hide(self) -> None:
        if self.window is None:
            return

        self.window.hide()

    def isVisible(self) -> bool:
        if self.window is None:
            return False

        return self.window.get_property("visible")
