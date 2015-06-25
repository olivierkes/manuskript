#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from models.outlineModel import *
from ui.editors.textFormat_ui import *
from functions import *

class textFormat(QWidget, Ui_textFormat):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self._textEdit = None
        
        formats = {
            "Bold":      [self.btnBold,       "format-text-bold",      self.tr("CTRL+B")],
            "Italic":    [self.btnItalic,     "format-text-italic",    self.tr("CTRL+I")],
            "Underline": [self.btnUnderlined, "format-text-underline", self.tr("CTRL+U")],
            "Clear":     [self.btnClear,      "edit-clear",            self.tr("CTRL+P")],
            "Left":      [self.btnLeft,       "format-justify-left",   self.tr("CTRL+L")],
            "Center":    [self.btnCenter,     "format-justify-center", self.tr("CTRL+E")],
            "Right":     [self.btnRight,      "format-justify-right",  self.tr("CTRL+R")],
            "Justify":   [self.btnJustify,    "format-justify-fill",   self.tr("CTRL+J")],
            }
        
        for f in formats:
            val = formats[f]
            a = QAction(QIcon.fromTheme(val[1]), f, self)
            a.setShortcut(val[2])
            a.setToolTip("Format {} ({})".format(f, val[2]))
            a.triggered.connect(self.setFormat)
            val[0].setDefaultAction(a)
    
    def setTextEdit(self, textEdit):
        self._textEdit = textEdit
        
    def updateFromIndex(self, index):
        if not index.isValid():
            self.setVisible(False)
            return
        
        if type(index.model()) != outlineModel:
            self.setVisible(False)
            return 
        
        self.setVisible(True)
        item = index.internalPointer()
        
        self.align.setVisible(True)
        self.format.setVisible(True)
        
        if item.isFolder():
            self.setVisible(False)
            return
        
        elif item.isText():
            self.align.setVisible(False)
            self.format.setVisible(False)
        elif item.isT2T():
            self.align.setVisible(False)
            
        
    def setFormat(self):
        act = self.sender()
        if self._textEdit:
            self._textEdit.applyFormat(act.text())