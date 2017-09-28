# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/about_ui.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
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
        self.buttonBox = QtWidgets.QDialogButtonBox(about)
        self.buttonBox.setGeometry(QtCore.QRect(20, 320, 391, 30))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.labelLogo = QtWidgets.QLabel(about)
        self.labelLogo.setGeometry(QtCore.QRect(30, 20, 381, 111))
        self.labelLogo.setText("")
        self.labelLogo.setPixmap(QtGui.QPixmap("../../icons/Manuskript/logo-400x104.png"))
        self.labelLogo.setObjectName("labelLogo")
        self.labelCopyright = QtWidgets.QLabel(about)
        self.labelCopyright.setGeometry(QtCore.QRect(70, 180, 361, 21))
        self.labelCopyright.setText("Copyright © 2015-2017 Olivier Keshavjee")
        self.labelCopyright.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelCopyright.setObjectName("labelCopyright")
        self.labelLicense = QtWidgets.QLabel(about)
        self.labelLicense.setGeometry(QtCore.QRect(70, 200, 361, 20))
        self.labelLicense.setText("GNU General Public License Version 3")
        self.labelLicense.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelLicense.setObjectName("labelLicense")
        self.labelManuskriptVersion = QtWidgets.QLabel(about)
        self.labelManuskriptVersion.setGeometry(QtCore.QRect(130, 130, 301, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelManuskriptVersion.setFont(font)
        self.labelManuskriptVersion.setText("Version")
        self.labelManuskriptVersion.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelManuskriptVersion.setObjectName("labelManuskriptVersion")
        self.labelSoftwareHeading = QtWidgets.QLabel(about)
        self.labelSoftwareHeading.setGeometry(QtCore.QRect(40, 240, 391, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelSoftwareHeading.setFont(font)
        self.labelSoftwareHeading.setText("Software Versions in Use:")
        self.labelSoftwareHeading.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelSoftwareHeading.setObjectName("labelSoftwareHeading")
        self.labelPythonVersion = QtWidgets.QLabel(about)
        self.labelPythonVersion.setGeometry(QtCore.QRect(70, 270, 361, 18))
        self.labelPythonVersion.setText("Python Version")
        self.labelPythonVersion.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelPythonVersion.setObjectName("labelPythonVersion")
        self.labelQtVersion = QtWidgets.QLabel(about)
        self.labelQtVersion.setGeometry(QtCore.QRect(70, 310, 361, 18))
        self.labelQtVersion.setText("Qt Version")
        self.labelQtVersion.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelQtVersion.setObjectName("labelQtVersion")
        self.labelPyQtVersion = QtWidgets.QLabel(about)
        self.labelPyQtVersion.setGeometry(QtCore.QRect(70, 290, 361, 18))
        self.labelPyQtVersion.setText("PyQt Version")
        self.labelPyQtVersion.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelPyQtVersion.setObjectName("labelPyQtVersion")
        self.labelWebsite = QtWidgets.QLabel(about)
        self.labelWebsite.setGeometry(QtCore.QRect(130, 150, 301, 20))
        self.labelWebsite.setText("http://www.theologeek.ch/manuskript/")
        self.labelWebsite.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.labelWebsite.setObjectName("labelWebsite")

        self.retranslateUi(about)
        self.buttonBox.accepted.connect(about.accept)
        QtCore.QMetaObject.connectSlotsByName(about)

    def retranslateUi(self, about):
        _translate = QtCore.QCoreApplication.translate
        about.setWindowTitle(_translate("about", "About Manuskript"))
        self.labelLogo.setToolTip(_translate("about", "Manuskript"))

