#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QVariant, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QTextEdit, QTableWidgetItem, QHeaderView

from manuskript import settings
from manuskript.enums import Outline
from manuskript.ui_qt.tools.frequency_ui import Ui_FrequencyAnalyzer
import re
from collections import Counter

class frequencyAnalyzer(QWidget, Ui_FrequencyAnalyzer):
    def __init__(self, mainWindow):
        QWidget.__init__(self)
        self.setupUi(self)
        self.mw = mainWindow

        self.splitter.setSizes([10, 100])
        self.splitter.setStretchFactor(1, 10)

        self.progressBarWord.hide()
        self.tblWord.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tblPhrase.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


        self.btnAnalyzeWord.clicked.connect(self.analyzeWord)
        self.btnAnalyzePhrase.clicked.connect(self.analyzePhrase)

        # Settings
        self.spnWordMin.setValue(settings.frequencyAnalyzer["wordMin"])
        self.txtWordExclude.setPlainText(settings.frequencyAnalyzer["wordExclude"])
        self.spnPhraseMin.setValue(settings.frequencyAnalyzer["phraseMin"])
        self.spnPhraseMax.setValue(settings.frequencyAnalyzer["phraseMax"])
        self.spnWordMin.valueChanged.connect(self.updateSettings)
        self.txtWordExclude.textChanged.connect(self.updateSettings)
        self.spnPhraseMin.valueChanged.connect(self.updateSettings)
        self.spnPhraseMax.valueChanged.connect(self.updateSettings)

    def analyzePhrase(self):
        root = self.mw.mdlOutline.rootItem
        nMin = self.spnPhraseMin.value()
        nMax = self.spnPhraseMax.value()

        def listPhrases(item, nMin, nMax):
            txt = item.text()

            # Split into words
            lst = re.findall(r"[\w']+", txt)            # Ignores punctuation
            # lst = re.findall(r"[\w']+|[.,!?;]", txt)  # Includes punctuation
            phrases = []

            # Make tuples of n-length
            for n in range(nMin, nMax + 1):
                for l in range(len(lst) - n + 1):
                    phrases.append(tuple(lst[l:l+n]))

            for c in item.children():
                phrases += listPhrases(c, nMin, nMax)

            return phrases

        lst = listPhrases(root, nMin, nMax)

        # Count
        count = Counter(lst)

        # Showing
        mdl = QStandardItemModel()
        mdl.setHorizontalHeaderLabels([self.tr("Phrases"), self.tr("Frequency")])
        for i in count.most_common():
            word = QStandardItem(" ".join(i[0]))
            number = QStandardItem()
            number.setData(i[1], Qt.DisplayRole)
            if i[1] > 1:
                mdl.appendRow([word, number])

        self.tblPhrase.setModel(mdl)

    def analyzeWord(self):
        root = self.mw.mdlOutline.rootItem

        exclude = self.txtWordExclude.toPlainText().split(",")
        exclude = [e.strip().lower() for e in exclude]

        def listWords(item):
            txt = item.text()

            lst = re.findall(r"[\w']+", txt)
            for c in item.children():
                lst += listWords(c)

            return lst

        lst = listWords(root)
        lst2 = []

        # Cleaning
        for i in lst:
            if len(i) >= self.spnWordMin.value() and not i.lower() in exclude:
                lst2.append(i.lower())

        # Count
        count = Counter(lst2)

        # Showing
        mdl = QStandardItemModel()
        mdl.setHorizontalHeaderLabels([self.tr("Word"), self.tr("Frequency")])
        for i in count.most_common():
            word = QStandardItem(i[0])
            number = QStandardItem()
            number.setData(i[1], Qt.DisplayRole)
            mdl.appendRow([word, number])

        self.tblWord.setModel(mdl)

    def updateSettings(self):
        settings.frequencyAnalyzer["wordMin"] = self.spnWordMin.value()
        settings.frequencyAnalyzer["wordExclude"] = self.txtWordExclude.toPlainText()
        settings.frequencyAnalyzer["phraseMin"] = self.spnPhraseMin.value()
        settings.frequencyAnalyzer["phraseMax"] = self.spnPhraseMax.value()
