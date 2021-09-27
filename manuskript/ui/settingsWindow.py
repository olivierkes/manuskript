#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Handy

Handy.init()

from manuskript.ui.abstractDialog import AbstractDialog

from manuskript.data import Settings
from manuskript.ui.settings import *


class SettingsWindow(AbstractDialog):

    @classmethod
    def packPage(cls, window, page_cls, settings: Settings):
        if window is None:
            return None

        try:
            page = page_cls(settings)
        except Exception as e:
            print(e)
            return None

        if page.widget is None:
            return None

        window.add(page.widget)
        return page

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/settings.glade", "settings_window")

        self.generalPage = None
        self.revisionsPage = None
        self.viewsPage = None
        self.labelsPage = None
        self.statusPage = None
        self.fullscreenPage = None

    def initWindow(self, builder, window):
        self.generalPage = SettingsWindow.packPage(window, GeneralPage, self.getSettings())
        self.revisionsPage = SettingsWindow.packPage(window, RevisionsPage, self.getSettings())
        self.viewsPage = SettingsWindow.packPage(window, ViewsPage, self.getSettings())
        self.labelsPage = SettingsWindow.packPage(window, LabelsPage, self.getSettings())
        self.statusPage = SettingsWindow.packPage(window, StatusPage, self.getSettings())
        self.fullscreenPage = SettingsWindow.packPage(window, FullscreenPage, self.getSettings())

    def getSettings(self) -> Settings:
        return self.mainWindow.getSettings()
