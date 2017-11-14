#!/usr/bin/env python
# --!-- coding: utf8 --!--
import json
import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFontMetrics, QFont
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QListWidgetItem, QTreeView

from manuskript.functions import mainWindow, writablePath
from manuskript.ui.exporters.manuskript.plainTextSettings_ui import Ui_exporterSettings
from manuskript.ui import style as S


class exporterSettings(QWidget, Ui_exporterSettings):
    def __init__(self, _format, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.toolBox.setStyleSheet(S.toolBoxSS())

        self.mw = mainWindow()
        self._format = _format
        self.settings = {}

        #################################################################
        # Content

        self.grpContentFilters.button.setChecked(False)

        h = self.tblContent.horizontalHeader()
        h.setSectionResizeMode(h.ResizeToContents)
        h.setSectionResizeMode(0, h.Stretch)

        self.contentUpdateTable()
        self.chkContentMore.toggled.connect(self.contentTableToggle)
        self.contentTableToggle(False)

        # Labels
        self.lstContentLabels.clear()
        h = QFontMetrics(self.font()).height()
        for i in range(0, self.mw.mdlLabels.rowCount()):
            item = self.mw.mdlLabels.item(i, 0)
            if item:
                item = QListWidgetItem(item.icon(), item.text())
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                item.setSizeHint(QSize(100, h))
                self.lstContentLabels.addItem(item)

        self.chkContentLabels.toggled.connect(self.lstContentLabels.setVisible)
        self.chkContentLabels.toggled.connect(lambda: self.listWidgetAdjustToContent(self.lstContentLabels))
        self.lstContentLabels.setVisible(False)

        # Status
        self.lstContentStatus.clear()
        h = QFontMetrics(self.font()).height()
        for i in range(0, self.mw.mdlStatus.rowCount()):
            item = self.mw.mdlStatus.item(i, 0)
            if item:
                item = QListWidgetItem(item.icon(), item.text())
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                item.setSizeHint(QSize(100, h))
                self.lstContentStatus.addItem(item)

        self.chkContentStatus.toggled.connect(self.lstContentStatus.setVisible)
        self.chkContentStatus.toggled.connect(lambda: self.listWidgetAdjustToContent(self.lstContentStatus))
        self.lstContentStatus.setVisible(False)

        # Root item
        self.cmbContentParent.setModel(self.mw.mdlOutline)
        v = QTreeView()
        self.cmbContentParent.setView(v)
        v.setHeaderHidden(True)
        for i in range(1, self.mw.mdlOutline.columnCount()):
            v.hideColumn(i)
        self.chkContentParent.toggled.connect(self.cmbContentParent.setVisible)
        self.cmbContentParent.hide()

        #################################################################
        # Separations

        for cmb in [self.cmbSepFF, self.cmbSepTT, self.cmbSepFT, self.cmbSepTF]:
            cmb.clear()

            cmb.addItem(self.tr("Empty line"), "empty")
            cmb.addItem(self.tr("Custom"), "custom")
            cmb.currentIndexChanged.connect(self.sepCmbChanged)

        #################################################################
        # Transformations

        h = self.tblReplacements.horizontalHeader()
        h.setSectionResizeMode(h.ResizeToContents)
        h.setSectionResizeMode(1, h.Stretch)
        h.setSectionResizeMode(2, h.Stretch)

        # Cf. https://en.wikipedia.org/wiki/Quotation_mark
        self.cmbTransDoubleQuotes.clear()
        self.cmbTransDoubleQuotes.addItems(["”___“", "“___”", "«___»"])
        self.cmbTransSingleQuote.clear()
        self.cmbTransSingleQuote.addItems(["‘___’", "‹___›"])

        for cmb in [self.cmbTransDoubleQuotes, self.cmbTransSingleQuote]:
            cmb.addItem(self.tr("Custom"), "custom")
            cmb.currentIndexChanged.connect(self.transCmbChanged)
            cmb.currentIndexChanged.emit(0)

        self.btnTransAdd.clicked.connect(lambda: self.transAddTableRow(checked=True))
        self.btnTransRemove.clicked.connect(self.transRemoveTableRow)
        self.tableWidgetAdjustToContent(self.tblReplacements)

        #################################################################
        # Preview

        self.cmbPreviewFont.setCurrentFont(self.font())
        self.spnPreviewSize.setValue(self.font().pointSize())

        #################################################################
        # Final stuff

        self.toolBox.setCurrentIndex(0)

    ###################################################################################################################
    # SETTINGS
    ###################################################################################################################

    def loadSettings(self):
        filename = self.getSettingsPath()
        if os.path.exists(filename):
            with open(filename) as f:
                self.settings = json.load(f)
            self.updateFromSettings()

        # Default values
        else:
            self.getSettings()

    def writeSettings(self):
        self.getSettings()
        with open(self.getSettingsPath(), 'w') as f:
            # json.dumps(json.loads(json.dumps(allSettings)), indent=4, sort_keys=True)
            json.dump(self.settings, f, indent=4, sort_keys=True)

    def getSettingsPath(self):
        return os.path.join(writablePath(), "exporter.ini")

    def updateFromSettings(self):
        settings = self.settings

        # Content
        s = settings["Content"]
        self.chkContentMore.setChecked(s["More"])

        if not s["More"]:
            self.tblContent.item(0, 1).setCheckState(Qt.Checked if s["FolderTitle"] else Qt.Unchecked)
            self.tblContent.item(1, 1).setCheckState(Qt.Checked if s["TextTitle"] else Qt.Unchecked)
            self.tblContent.item(1, 2).setCheckState(Qt.Checked if s["TextText"] else Qt.Unchecked)

        else:
            nLevel = len(s["FolderTitle"])
            for i in range(nLevel):
                item = self.tblContent.item(i + 2, 1)
                if item:
                    item.setCheckState(Qt.Checked if s["FolderTitle"][i] else Qt.Unchecked)
                item = self.tblContent.item(i + 2 + nLevel, 1)
                if item:
                    item.setCheckState(Qt.Checked if s["TextTitle"][i] else Qt.Unchecked)
                item = self.tblContent.item(i + 2 + nLevel, 2)
                if item:
                    item.setCheckState(Qt.Checked if s["TextText"][i] else Qt.Unchecked)

        self.chkContentIgnoreCompile.setChecked(s["IgnoreCompile"])
        self.chkContentParent.setChecked(s["Parent"])
        self.chkContentLabels.setChecked(s["Labels"])
        self.chkContentStatus.setChecked(s["Status"])
        # FIXME: parent, labels, status

        # Separations
        s = settings["Separator"]
        for val, cmb, txt in [
            ("FF", self.cmbSepFF, self.txtSepFF),
            ("TT", self.cmbSepTT, self.txtSepTT),
            ("FT", self.cmbSepFT, self.txtSepFT),
            ("TF", self.cmbSepTF, self.txtSepTF),
        ]:
            if s[val] == "\n":
                cmb.setCurrentIndex(0)
            else:
                cmb.setCurrentIndex(1)
                txt.setText(self._format.escapes(s[val]))

        # Transformations
        s = settings["Transform"]
        self.chkTransEllipse.setChecked(s["Ellipse"])
        self.chkTransDash.setChecked(s["Dash"])

        for val, chk, cmb, txtA, txtB in [
            ("DoubleQuotes", self.chkTransDoubleQuotes, self.cmbTransDoubleQuotes, self.txtTransDoubleQuotesA, self.txtTransDoubleQuotesB),
            ("SingleQuote",  self.chkTransSingleQuote,  self.cmbTransSingleQuote,  self.txtTransSingleQuoteA,  self.txtTransSingleQuoteB),
        ]:
            chk.setChecked(s[val] != False)
            if s[val]:
                if cmb.findText(s[val]) != -1:
                    cmb.setCurrentText(s[val])
                else:
                    cmb.setCurrentIndex(cmb.count() - 1)
                    txtA.setText(s[val].split("___")[0])
                    txtB.setText(s[val].split("___")[1])

        self.chkTransSpaces.setChecked(s["Spaces"])

        for i in s["Custom"]:
            self.transAddTableRow(i[0], i[1], i[2], i[3])

        # Preview
        s = settings["Preview"]
        f = QFont()
        f.fromString(s["PreviewFont"])
        self.cmbPreviewFont.setCurrentFont(f)
        self.spnPreviewSize.setValue(f.pointSize())

    def getSettings(self):
        """Updates settings from ui, and return."""
        # Content
        s = self.settings.get("Content", {})
        s["More"] = self.chkContentMore.isChecked()

        if not s["More"]:
            s["FolderTitle"] = self.tblContent.item(0, 1).checkState() == Qt.Checked
            s["TextTitle"] = self.tblContent.item(1, 1).checkState() == Qt.Checked
            s["TextText"] = self.tblContent.item(1, 2).checkState() == Qt.Checked

        else:
            s["FolderTitle"] = []
            s["TextTitle"] = []
            s["TextText"] = []
            nLevel = int((self.tblContent.rowCount() - 2) / 2)
            for row in range(nLevel):
                s["FolderTitle"].append(self.tblContent.item(2 + row, 1).checkState() == Qt.Checked)
                s["TextTitle"].append(self.tblContent.item(2 + row + nLevel, 1).checkState() == Qt.Checked)
                s["TextText"].append(self.tblContent.item(2 + row + nLevel, 2).checkState() == Qt.Checked)

        s["IgnoreCompile"] = self.chkContentIgnoreCompile.isChecked()
        s["Parent"] = self.chkContentParent.isChecked()
        s["Labels"] = self.chkContentLabels.isChecked()
        s["Status"] = self.chkContentStatus.isChecked()
        self.settings["Content"] = s
        # FIXME: parent, labels, status

        # Separations
        s = self.settings.get("Separator", {})
        for val, cmb, txt in [
            ("FF", self.cmbSepFF, self.txtSepFF),
            ("TT", self.cmbSepTT, self.txtSepTT),
            ("FT", self.cmbSepFT, self.txtSepFT),
            ("TF", self.cmbSepTF, self.txtSepTF),
        ]:
            if cmb.currentIndex() == 0:
                s[val] = "\n"

            else:
                s[val] = self._format.descapes(txt.text())
        self.settings["Separator"] = s

        # Transformations
        s = self.settings.get("Transform", {})
        s["Ellipse"] = self.chkTransEllipse.isChecked()
        s["Dash"] = self.chkTransDash.isChecked()

        for val, chk, cmb, txtA, txtB in [
            ("DoubleQuotes", self.chkTransDoubleQuotes, self.cmbTransDoubleQuotes, self.txtTransDoubleQuotesA, self.txtTransDoubleQuotesB),
            ("SingleQuote", self.chkTransSingleQuote, self.cmbTransSingleQuote, self.txtTransSingleQuoteA, self.txtTransSingleQuoteB),
        ]:
            if not chk.isChecked():
                s[val] = False
            else:
                if cmb.currentData() == "custom":
                    s[val] = txtA.text() + "___" + txtB.text()
                else:
                    s[val] = cmb.currentText()

        s["Spaces"] = self.chkTransSpaces.isChecked()

        s["Custom"] = []
        for i in range(self.tblReplacements.rowCount()):
            s["Custom"].append(self.getTableRowValues(self.tblReplacements, i))
        self.settings["Transform"] = s

        # Preview
        s = self.settings.get("Preview", {})
        f = self.cmbPreviewFont.currentFont()
        f.setPointSize(self.spnPreviewSize.value())
        s["PreviewFont"] = f.toString()
        self.settings["Preview"] = s

        return self.settings

    def sepCmbChanged(self, index):
        cmb = self.sender()
        map = {
            self.cmbSepFF: self.txtSepFF,
            self.cmbSepTT: self.txtSepTT,
            self.cmbSepFT: self.txtSepFT,
            self.cmbSepTF: self.txtSepTF
        }
        map[cmb].setEnabled(cmb.currentData() == "custom")

    def transCmbChanged(self, index):
        cmb = self.sender()
        map = {
            self.cmbTransDoubleQuotes: (self.txtTransDoubleQuotesA, self.lblTransDoubleQuotes, self.txtTransDoubleQuotesB),
            self.cmbTransSingleQuote:  (self.txtTransSingleQuoteA,  self.lblTransSingleQuote,  self.txtTransSingleQuoteB),
        }
        for txt in map[cmb]:
            txt.setVisible(cmb.currentData() == "custom")

    def contentUpdateTable(self):

        def addFolderRow(text=self.tr("Folder")):
            self.tableWidgetAddRow(self.tblContent, [
                self.tableWidgetMakeItem(text, "folder"),
                self.tableWidgetMakeItem("", "", True, True),
            ])

        def addTextRow(text=self.tr("Text")):
            self.tableWidgetAddRow(self.tblContent, [
                self.tableWidgetMakeItem(text, "text-x-generic"),
                self.tableWidgetMakeItem("", "", True, False),
                self.tableWidgetMakeItem("", "", True, True),
            ])

        self.tblContent.setRowCount(0)

        # Basic
        addFolderRow()
        addTextRow()

        # Detailed
        level = self.mw.mdlOutline.maxLevel()

        for i in range(level):
            addFolderRow(self.tr("{}Level {} folder").format("  " * i, i + 1))

        for i in range(level):
            addTextRow(self.tr("{}Level {} text").format("  " * i, i + 1))

        self.tableWidgetAdjustToContent(self.tblContent)

    def contentTableToggle(self, detailed):
        for i in range(self.tblContent.rowCount()):
            self.tblContent.setRowHidden(i, i in [0, 1] and detailed or (not i in [0, 1] and not detailed))
        self.tableWidgetAdjustToContent(self.tblContent)

    def getTableRowValues(self, table, row):
        r = []
        for col in range(table.columnCount()):
            item = table.item(row, col)

            if not item:
                r.append(None)
            elif item.flags() & Qt.ItemIsUserCheckable == Qt.ItemIsUserCheckable:
                r.append(item.checkState() == Qt.Checked)
            else:
                r.append(item.text())

        return r

    def transAddTableRow(self, checked=True, A="", B="", regexp=False):
        self.tableWidgetAddRow(self.tblReplacements, [
            self.tableWidgetMakeItem("", "", True,  checked),
            self.tableWidgetMakeItem(A, "", False, False),
            self.tableWidgetMakeItem(B, "", False, False),
            self.tableWidgetMakeItem("", "", True,  regexp),
        ])
        self.tableWidgetAdjustToContent(self.tblReplacements)

    def transRemoveTableRow(self):
        self.tblReplacements.removeRow(self.tblReplacements.currentRow())
        self.tableWidgetAdjustToContent(self.tblReplacements)

    def tableWidgetMakeItem(self, text="", icon="", checkable=False, checked=False):
        """Creates a QTableWidgetItem with the given attributes."""
        item = QTableWidgetItem(QIcon.fromTheme(icon), text)
        if checkable:
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        else:
            item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)

        return item

    def tableWidgetAddRow(self, table, items):
        """Appends the given items (list of QTableWidgetItems) to table."""
        table.setRowCount(table.rowCount() + 1)
        k = 0
        for i in items:
            table.setItem(table.rowCount() - 1, k, i)
            k += 1

    def tableWidgetAdjustToContent(self, table):
        """Set sizehint of QTableWidget table so that it matches content vertically."""

        h = 0

        h += table.horizontalHeader().height()

        for i in range(table.rowCount()):
            h += table.rowHeight(i)

        table.setMinimumSize(QSize(0, h + 2))
        table.setMaximumSize(QSize(16777215, h + 2))

    def listWidgetAdjustToContent(self, lst):
        """Adjust listWidget to content."""
        h = 0
        for i in range(lst.count()):
            h += lst.item(i).sizeHint().height()

        lst.setMinimumSize(QSize(0, h+2))
        lst.setMaximumSize(QSize(16777215, h+2))



