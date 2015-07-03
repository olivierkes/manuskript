# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/views/metadataView_ui.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_metadataView(object):
    def setupUi(self, metadataView):
        metadataView.setObjectName("metadataView")
        metadataView.resize(400, 537)
        self.verticalLayout = QtWidgets.QVBoxLayout(metadataView)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_4 = collapsibleGroupBox2(metadataView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setFlat(True)
        self.groupBox_4.setCheckable(True)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_28 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_28.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_28.setObjectName("verticalLayout_28")
        self.properties = propertiesView(self.groupBox_4)
        self.properties.setMinimumSize(QtCore.QSize(0, 50))
        self.properties.setObjectName("properties")
        self.verticalLayout_28.addWidget(self.properties)
        self.verticalLayout.addWidget(self.groupBox_4)
        self.groupBox_5 = collapsibleGroupBox2(metadataView)
        self.groupBox_5.setFlat(True)
        self.groupBox_5.setCheckable(True)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_22 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.txtSummarySentance = lineEditView(self.groupBox_5)
        self.txtSummarySentance.setInputMask("")
        self.txtSummarySentance.setObjectName("txtSummarySentance")
        self.verticalLayout_22.addWidget(self.txtSummarySentance)
        self.txtSummaryFull = textEditView(self.groupBox_5)
        self.txtSummaryFull.setObjectName("txtSummaryFull")
        self.verticalLayout_22.addWidget(self.txtSummaryFull)
        self.verticalLayout.addWidget(self.groupBox_5)
        self.groupBox_6 = collapsibleGroupBox2(metadataView)
        self.groupBox_6.setFlat(True)
        self.groupBox_6.setCheckable(True)
        self.groupBox_6.setObjectName("groupBox_6")
        self.horizontalLayout_29 = QtWidgets.QHBoxLayout(self.groupBox_6)
        self.horizontalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_29.setObjectName("horizontalLayout_29")
        self.txtNotes = textEditCompleter(self.groupBox_6)
        self.txtNotes.setObjectName("txtNotes")
        self.horizontalLayout_29.addWidget(self.txtNotes)
        self.verticalLayout.addWidget(self.groupBox_6)
        self.groupBox_7 = collapsibleGroupBox2(metadataView)
        self.groupBox_7.setFlat(True)
        self.groupBox_7.setCheckable(True)
        self.groupBox_7.setObjectName("groupBox_7")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_7)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.revisions = revisions(self.groupBox_7)
        self.revisions.setMinimumSize(QtCore.QSize(0, 50))
        self.revisions.setObjectName("revisions")
        self.verticalLayout_2.addWidget(self.revisions)
        self.verticalLayout.addWidget(self.groupBox_7)

        self.retranslateUi(metadataView)
        QtCore.QMetaObject.connectSlotsByName(metadataView)

    def retranslateUi(self, metadataView):
        _translate = QtCore.QCoreApplication.translate
        metadataView.setWindowTitle(_translate("metadataView", "Form"))
        self.groupBox_4.setTitle(_translate("metadataView", "Properties"))
        self.groupBox_5.setTitle(_translate("metadataView", "Summary"))
        self.txtSummarySentance.setPlaceholderText(_translate("metadataView", "One line summary"))
        self.groupBox_6.setTitle(_translate("metadataView", "Notes / References"))
        self.groupBox_7.setTitle(_translate("metadataView", "Revisions"))

from ui.views.textEditCompleter import textEditCompleter
from ui.views.textEditView import textEditView
from ui.views.propertiesView import propertiesView
from ui.views.lineEditView import lineEditView
from ui.revisions import revisions
from ui.collapsibleGroupBox2 import collapsibleGroupBox2
