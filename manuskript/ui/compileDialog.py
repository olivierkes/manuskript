#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, qApp, QFileDialog

from manuskript import exporter
from manuskript.ui.compileDialog_ui import Ui_compileDialog


class compileDialog(QDialog, Ui_compileDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.btnPath.clicked.connect(self.getPath)
        self.btnFilename.clicked.connect(self.getFilename)

        self.btnCompile.clicked.connect(self.doCompile)
        self.cmbTargets.activated.connect(self.updateUI)

        self.txtPath.setText("/home/olivier/Documents/Travail/Geekeries/Python/manuskript/ExportTest")
        self.txtFilename.setText("/home/olivier/Documents/Travail/Geekeries/Python/manuskript/ExportTest/test.html")

        self.populatesTarget()
        self.updateUI()

    ###############################################################################
    # UI
    ###############################################################################

    def populatesTarget(self):
        for code in exporter.formats:
            self.cmbTargets.addItem(exporter.formats[code][0], code)

    def updateUI(self):
        target = self.cmbTargets.currentData()

        if not exporter.formats[target][1]:
            self.btnCompile.setEnabled(False)
            requires = []
        else:
            self.btnCompile.setEnabled(True)
            requires = exporter.formats[target][1].requires

        self.wPath.setVisible("path" in requires)
        self.wFilename.setVisible("filename" in requires)

    def startWorking(self):
        # Setting override cursor
        qApp.setOverrideCursor(Qt.WaitCursor)

        # Button
        self.btnCompile.setEnabled(False)
        self.txtBtn = self.btnCompile.text()
        self.btnCompile.setText(self.tr("Working..."))

    def stopWorking(self):
        # Removing override cursor
        qApp.restoreOverrideCursor()

        # Button
        self.btnCompile.setEnabled(True)
        self.btnCompile.setText(self.txtBtn)

    ###############################################################################
    # USER INPUTS
    ###############################################################################

    def getPath(self):
        path = self.txtPath.text()
        path = QFileDialog.getExistingDirectory(self, self.tr("Chose export folder"), path)
        if path:
            self.txtPath.setText(path)

    def getFilename(self):
        fn = self.txtFilename.text()
        target = self.cmbTargets.currentData()
        fltr = exporter.formats[target][2]
        fn = QFileDialog.getSaveFileName(self, self.tr("Chose export target"), fn, fltr)

        if fn[0]:
            self.txtFilename.setText(fn[0])


        ###############################################################################
        # COMPILE
        ###############################################################################

    def doCompile(self):
        target = self.cmbTargets.currentData()

        self.startWorking()

        if target == "arbo":
            compiler = exporter.formats[target][1]()
            compiler.doCompile(self.txtPath.text())

        elif target in ["html", "odt"]:
            compiler = exporter.formats[target][1]()
            compiler.doCompile(self.txtFilename.text())

        self.stopWorking()
