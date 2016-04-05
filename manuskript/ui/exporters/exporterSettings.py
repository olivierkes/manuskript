#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFontMetrics
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QListWidgetItem, QTreeView

from manuskript.functions import mainWindow
from manuskript.ui.exporters.exporterSettings_ui import Ui_exporterSettings


class exporterSettings(QWidget, Ui_exporterSettings):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.mw = mainWindow()

        self.grpContentFilters.setCustomColors(active="lightBlue", inactive="lightgray")

        self.grpContentFilters.button.setChecked(False)

        #################################################################
        # Content

        h = self.tblContent.horizontalHeader()
        h.setSectionResizeMode(h.ResizeToContents)
        h.setSectionResizeMode(0, h.Stretch)

        self.contentUpdateTable()
        self.chkContentMore.toggled.connect(self.contentUpdateTable)

        # Labels
        self.lstContentLabels.clear()
        h = QFontMetrics(self.font()).height()
        for i in range(1, self.mw.mdlLabels.rowCount()):
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
        for i in range(1, self.mw.mdlStatus.rowCount()):
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
        self.cmbTransDoubleQuotes.addItems(["” “", "“ ”", "« »"])
        self.cmbTransSingleQuote.clear()
        self.cmbTransSingleQuote.addItems(["‘ ’", "‹ ›"])


        for cmb in [self.cmbTransDoubleQuotes, self.cmbTransSingleQuote]:
            cmb.addItem(self.tr("Custom"), "custom")
            cmb.currentIndexChanged.connect(self.transCmbChanged)
            cmb.currentIndexChanged.emit(0)

        self.btnTransAdd.clicked.connect(self.transAddTableRow)
        self.btnTransRemove.clicked.connect(self.transRemoveTableRow)

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

    def contentUpdateTable(self, val=False):

        def addFolderRow(text="Folder"):
            self.tableWidgetAddRow(self.tblContent, [
                self.tableWidgetMakeItem(text, "folder"),
                self.tableWidgetMakeItem("", "", True, True),
            ])

        def addTextRow(text="Text"):
            self.tableWidgetAddRow(self.tblContent, [
                self.tableWidgetMakeItem(text, "text-x-generic"),
                self.tableWidgetMakeItem("", "", True, False),
                self.tableWidgetMakeItem("", "", True, True),
            ])

        # self.tblContent.clearContents()
        self.tblContent.setRowCount(0)

        if not val:
            addFolderRow()
            addTextRow()

        else:
            level = self.mw.mdlOutline.maxLevel()

            for i in range(level):
                addFolderRow("{}Level {} folder".format("  " * i, i + 1))

            for i in range(level):
                addTextRow("{}Level {} text".format("  " * i, i + 1))

        self.tableWidgetAdjustToContent(self.tblContent)


    def transAddTableRow(self):
        self.tableWidgetAddRow(self.tblReplacements, [
            self.tableWidgetMakeItem("", "", True,  True),
            self.tableWidgetMakeItem("", "", False, False),
            self.tableWidgetMakeItem("", "", False, False),
            self.tableWidgetMakeItem("", "", True,  False),
        ])

    def transRemoveTableRow(self):
        self.tblReplacements.removeRow(self.tblReplacements.currentRow())

    def tableWidgetMakeItem(self, text="", icon="", checkable=False, checked=False):
        """Creates a QTableWidgetItem with the given attributes."""
        item = QTableWidgetItem(QIcon.fromTheme(icon), text)
        if checkable:
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)

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



