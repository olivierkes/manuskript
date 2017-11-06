#!/usr/bin/env python
# --!-- coding: utf8 --!--
import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QWidget

from manuskript import exporter
from manuskript.functions import lightBlue, writablePath
from manuskript.ui.importers.importer_ui import Ui_importer


class importerDialog(QWidget, Ui_importer):
    def __init__(self, parent=None, mw=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        # Var
        self.mw = mw

        #TODO
