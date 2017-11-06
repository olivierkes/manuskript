# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/importers/importer_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_importer(object):
    def setupUi(self, importer):
        importer.setObjectName("importer")
        importer.resize(694, 489)
        self.verticalLayout = QtWidgets.QVBoxLayout(importer)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(importer)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.cmbImporters = QtWidgets.QComboBox(importer)
        self.cmbImporters.setObjectName("cmbImporters")
        self.horizontalLayout.addWidget(self.cmbImporters)
        self.btnManageImporters = QtWidgets.QPushButton(importer)
        icon = QtGui.QIcon.fromTheme("preferences-system")
        self.btnManageImporters.setIcon(icon)
        self.btnManageImporters.setObjectName("btnManageImporters")
        self.horizontalLayout.addWidget(self.btnManageImporters)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnChoseFile = QtWidgets.QPushButton(importer)
        icon = QtGui.QIcon.fromTheme("document-import")
        self.btnChoseFile.setIcon(icon)
        self.btnChoseFile.setObjectName("btnChoseFile")
        self.horizontalLayout.addWidget(self.btnChoseFile)
        self.btnPreview = QtWidgets.QPushButton(importer)
        icon = QtGui.QIcon.fromTheme("document-print-preview")
        self.btnPreview.setIcon(icon)
        self.btnPreview.setObjectName("btnPreview")
        self.horizontalLayout.addWidget(self.btnPreview)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.splitter = QtWidgets.QSplitter(importer)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.grpSettings = QtWidgets.QGroupBox(self.splitter)
        self.grpSettings.setObjectName("grpSettings")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.grpSettings)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.grpPreview = QtWidgets.QGroupBox(self.splitter)
        self.grpPreview.setObjectName("grpPreview")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.grpPreview)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(importer)
        QtCore.QMetaObject.connectSlotsByName(importer)

    def retranslateUi(self, importer):
        _translate = QtCore.QCoreApplication.translate
        importer.setWindowTitle(_translate("importer", "Import"))
        self.label.setText(_translate("importer", "Import from:"))
        self.btnManageImporters.setText(_translate("importer", "Manage importers"))
        self.btnChoseFile.setText(_translate("importer", "Chose file"))
        self.btnPreview.setText(_translate("importer", "Preview"))
        self.grpSettings.setTitle(_translate("importer", "Settings"))
        self.grpPreview.setTitle(_translate("importer", "Preview"))

