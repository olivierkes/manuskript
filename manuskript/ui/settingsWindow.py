#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from manuskript.ui.abstractDialog import AbstractDialog


class SettingsWindow(AbstractDialog):

    def __init__(self, mainWindow):
        AbstractDialog.__init__(self, mainWindow, "ui/settings.glade", "settings_window")
