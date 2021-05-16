#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QLabel, QSizePolicy


class statusLabel(QLabel):
    def __init__(self, text=None, parent=None):
        QLabel.__init__(self, text=text, parent=parent)

        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        self.hide()
