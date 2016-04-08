# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/exporters/exporter_ui.ui'
#
# Created: Fri Apr  8 12:22:37 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_exporter(object):
    def setupUi(self, exporter):
        exporter.setObjectName("exporter")
        exporter.resize(933, 642)
        self.verticalLayout = QtWidgets.QVBoxLayout(exporter)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(exporter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.cmbExporters = QtWidgets.QComboBox(exporter)
        self.cmbExporters.setObjectName("cmbExporters")
        self.horizontalLayout.addWidget(self.cmbExporters)
        self.btnManageExporters = QtWidgets.QPushButton(exporter)
        icon = QtGui.QIcon.fromTheme("preferences-system")
        self.btnManageExporters.setIcon(icon)
        self.btnManageExporters.setObjectName("btnManageExporters")
        self.horizontalLayout.addWidget(self.btnManageExporters)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnPreview = QtWidgets.QPushButton(exporter)
        icon = QtGui.QIcon.fromTheme("document-print-preview")
        self.btnPreview.setIcon(icon)
        self.btnPreview.setObjectName("btnPreview")
        self.horizontalLayout.addWidget(self.btnPreview)
        self.btnExport = QtWidgets.QPushButton(exporter)
        icon = QtGui.QIcon.fromTheme("document-export")
        self.btnExport.setIcon(icon)
        self.btnExport.setObjectName("btnExport")
        self.horizontalLayout.addWidget(self.btnExport)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.splitter = QtWidgets.QSplitter(exporter)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.grpSettings = QtWidgets.QGroupBox(self.splitter)
        self.grpSettings.setObjectName("grpSettings")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.grpSettings)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.grpPreview = QtWidgets.QGroupBox(self.splitter)
        self.grpPreview.setObjectName("grpPreview")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.grpPreview)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(exporter)
        QtCore.QMetaObject.connectSlotsByName(exporter)

    def retranslateUi(self, exporter):
        _translate = QtCore.QCoreApplication.translate
        exporter.setWindowTitle(_translate("exporter", "Export"))
        self.label.setText(_translate("exporter", "Export to:"))
        self.btnManageExporters.setText(_translate("exporter", "Manage exporters"))
        self.btnPreview.setText(_translate("exporter", "Preview"))
        self.btnExport.setText(_translate("exporter", "Export"))
        self.grpSettings.setTitle(_translate("exporter", "Settings"))
        self.grpPreview.setTitle(_translate("exporter", "Preview"))

