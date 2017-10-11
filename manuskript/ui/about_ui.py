# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/about_ui.ui'
#
# Created: Wed Oct 11 08:28:24 2017
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_about(object):
    def setupUi(self, about):
        about.setObjectName("about")
        about.setWindowModality(QtCore.Qt.ApplicationModal)
        about.resize(445, 370)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../icons/Manuskript/icon-64px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        about.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(about)
        self.gridLayout.setObjectName("gridLayout")
        self.labelManuskriptVersion = QtWidgets.QLabel(about)
        self.labelManuskriptVersion.setText("Version")
        self.labelManuskriptVersion.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelManuskriptVersion.setObjectName("labelManuskriptVersion")
        self.gridLayout.addWidget(self.labelManuskriptVersion, 2, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.labelLogo = QtWidgets.QLabel(about)
        self.labelLogo.setText("")
        self.labelLogo.setPixmap(QtGui.QPixmap("../../icons/Manuskript/logo-400x104.png"))
        self.labelLogo.setObjectName("labelLogo")
        self.gridLayout.addWidget(self.labelLogo, 0, 0, 1, 2)
        self.labelSoftwareVersion = QtWidgets.QLabel(about)
        self.labelSoftwareVersion.setText("Software Versions in Use:")
        self.labelSoftwareVersion.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.labelSoftwareVersion.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelSoftwareVersion.setObjectName("labelSoftwareVersion")
        self.gridLayout.addWidget(self.labelSoftwareVersion, 4, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(about)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 1)

        self.retranslateUi(about)
        self.buttonBox.accepted.connect(about.accept)
        QtCore.QMetaObject.connectSlotsByName(about)

    def retranslateUi(self, about):
        _translate = QtCore.QCoreApplication.translate
        about.setWindowTitle(_translate("about", "About Manuskript"))
        self.labelLogo.setToolTip(_translate("about", "Manuskript"))

