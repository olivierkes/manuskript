# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/views/metadataView_ui.ui'
#
# Created: Fri Apr  8 14:24:47 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_metadataView(object):
    def setupUi(self, metadataView):
        metadataView.setObjectName("metadataView")
        metadataView.resize(400, 537)
        self.verticalLayout = QtWidgets.QVBoxLayout(metadataView)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.grpProperties = collapsibleGroupBox2(metadataView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpProperties.sizePolicy().hasHeightForWidth())
        self.grpProperties.setSizePolicy(sizePolicy)
        self.grpProperties.setFlat(True)
        self.grpProperties.setCheckable(True)
        self.grpProperties.setObjectName("grpProperties")
        self.verticalLayout_28 = QtWidgets.QVBoxLayout(self.grpProperties)
        self.verticalLayout_28.setSpacing(0)
        self.verticalLayout_28.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_28.setObjectName("verticalLayout_28")
        self.properties = propertiesView(self.grpProperties)
        self.properties.setMinimumSize(QtCore.QSize(0, 50))
        self.properties.setObjectName("properties")
        self.verticalLayout_28.addWidget(self.properties)
        self.verticalLayout.addWidget(self.grpProperties)
        self.grpSummary = collapsibleGroupBox2(metadataView)
        self.grpSummary.setFlat(True)
        self.grpSummary.setCheckable(True)
        self.grpSummary.setObjectName("grpSummary")
        self.verticalLayout_22 = QtWidgets.QVBoxLayout(self.grpSummary)
        self.verticalLayout_22.setSpacing(0)
        self.verticalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.txtSummarySentence = lineEditView(self.grpSummary)
        self.txtSummarySentence.setInputMask("")
        self.txtSummarySentence.setFrame(False)
        self.txtSummarySentence.setObjectName("txtSummarySentence")
        self.verticalLayout_22.addWidget(self.txtSummarySentence)
        self.line = QtWidgets.QFrame(self.grpSummary)
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(0)
        self.line.setMidLineWidth(0)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_22.addWidget(self.line)
        self.txtSummaryFull = textEditView(self.grpSummary)
        self.txtSummaryFull.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.txtSummaryFull.setObjectName("txtSummaryFull")
        self.verticalLayout_22.addWidget(self.txtSummaryFull)
        self.verticalLayout.addWidget(self.grpSummary)
        self.grpNotes = collapsibleGroupBox2(metadataView)
        self.grpNotes.setFlat(True)
        self.grpNotes.setCheckable(True)
        self.grpNotes.setObjectName("grpNotes")
        self.horizontalLayout_29 = QtWidgets.QHBoxLayout(self.grpNotes)
        self.horizontalLayout_29.setSpacing(0)
        self.horizontalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_29.setObjectName("horizontalLayout_29")
        self.txtNotes = textEditCompleter(self.grpNotes)
        self.txtNotes.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.txtNotes.setObjectName("txtNotes")
        self.horizontalLayout_29.addWidget(self.txtNotes)
        self.verticalLayout.addWidget(self.grpNotes)
        self.grpRevisions = collapsibleGroupBox2(metadataView)
        self.grpRevisions.setFlat(True)
        self.grpRevisions.setCheckable(True)
        self.grpRevisions.setObjectName("grpRevisions")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.grpRevisions)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.revisions = revisions(self.grpRevisions)
        self.revisions.setMinimumSize(QtCore.QSize(0, 50))
        self.revisions.setObjectName("revisions")
        self.verticalLayout_2.addWidget(self.revisions)
        self.verticalLayout.addWidget(self.grpRevisions)

        self.retranslateUi(metadataView)
        QtCore.QMetaObject.connectSlotsByName(metadataView)

    def retranslateUi(self, metadataView):
        _translate = QtCore.QCoreApplication.translate
        metadataView.setWindowTitle(_translate("metadataView", "Form"))
        self.grpProperties.setTitle(_translate("metadataView", "Properties"))
        self.grpSummary.setTitle(_translate("metadataView", "Summary"))
        self.txtSummarySentence.setPlaceholderText(_translate("metadataView", "One line summary"))
        self.txtSummaryFull.setPlaceholderText(_translate("metadataView", "Full summary"))
        self.grpNotes.setTitle(_translate("metadataView", "Notes / References"))
        self.txtNotes.setPlaceholderText(_translate("metadataView", "Notes / References"))
        self.grpRevisions.setTitle(_translate("metadataView", "Revisions"))

from manuskript.ui.collapsibleGroupBox2 import collapsibleGroupBox2
from manuskript.ui.views.textEditView import textEditView
from manuskript.ui.views.textEditCompleter import textEditCompleter
from manuskript.ui.views.propertiesView import propertiesView
from manuskript.ui.views.lineEditView import lineEditView
from manuskript.ui.revisions import revisions
