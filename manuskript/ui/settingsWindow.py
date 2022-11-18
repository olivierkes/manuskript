#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Handy

Handy.init()

from manuskript.ui.abstractDialog import AbstractDialog

from manuskript.data import Project, Settings
from manuskript.ui.settings import *


class SettingsWindow(AbstractDialog):

    @classmethod
    def packPage(cls, window, page_cls, settings: Settings, data=None):
        if window is None:
            return None

        try:
            if data is None:
                page = page_cls(settings)
            else:
                page = page_cls(settings, data)
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
        project = self.getProject()
        settings = self.getSettings()

        self.generalPage = SettingsWindow.packPage(window, GeneralPage, settings)
        self.revisionsPage = SettingsWindow.packPage(window, RevisionsPage, settings)
        self.viewsPage = SettingsWindow.packPage(window, ViewsPage, settings)
        self.labelsPage = SettingsWindow.packPage(window, LabelsPage, settings, project.labels)
        self.statusPage = SettingsWindow.packPage(window, StatusPage, settings, project.statuses)
        self.fullscreenPage = SettingsWindow.packPage(window, FullscreenPage, settings)

    def getSettings(self) -> Settings:
        return self.mainWindow.getSettings()

    def getProject(self) -> Project:
        return self.mainWindow.getProject()
