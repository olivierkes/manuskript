#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Handy", "1")
gi.require_version("GdkPixbuf", "2.0")
# TODO : I don't have access to WebKit2 4.0
try:
    gi.require_version("WebKit2", "4.1")
except ValueError:
    gi.require_version("WebKit2", "4.0")

from gi.repository import GObject, Gtk, Handy

Handy.init()

from manuskript.util import Translation
from manuskript.ui.util import *

from manuskript.ui.aboutDialog import AboutDialog
from manuskript.ui.compileWindow import CompileWindow
from manuskript.ui.importWindow import ImportWindow
from manuskript.ui.mainWindow import MainWindow
from manuskript.ui.settingsWindow import SettingsWindow
from manuskript.ui.startupWindow import StartupWindow
