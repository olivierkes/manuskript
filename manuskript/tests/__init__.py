#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests."""

# METHOD 1
# ========
# Don't know why, this causes seg fault on SemaphoreCI
# Seg fault in app = QApplication(...)
# Workaround: create and discard an app first...
from PyQt5.QtWidgets import QApplication
QApplication([])

# Create app and mainWindow
from manuskript import main
app, MW = main.prepare(tests=True)

# FIXME: Again, don't know why, but when closing a project and then reopening
#        one, we get a `TypeError: connection is not unique` in MainWindow:
#        self.btnAddSubPlot.clicked.connect(self.updateSubPlotView, F.AUC)
#        Yet the disconnectAll() function has been called.
#        Workaround: we remove the necessity for connection to be unique. This
#        works for now, but could create issues later one when we want to tests
#        those specific functionnality. Maybe it will be called several times.
#        At that moment, we will need to catch the exception in the MainWindow,
#        or better: understand why it happens at all, and only on some signals.
from manuskript import functions as F
from PyQt5.QtCore import Qt
F.AUC = Qt.AutoConnection

# METHOD 2
# ========
# We need a qApplication to be running, or all the calls to qApp
# will throw a seg fault.
# from PyQt5.QtWidgets import QApplication
# app = QApplication([])
# app.setOrganizationName("manuskript_tests")
# app.setApplicationName("manuskript_tests")

# from manuskript.mainWindow import MainWindow
# MW = MainWindow()
