# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'listDialog_ui.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GenericListDialog(object):
    def setupUi(self, GenericListDialog):
        GenericListDialog.setObjectName("GenericListDialog")
        GenericListDialog.resize(451, 340)
        GenericListDialog.setModal(False)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(GenericListDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(GenericListDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.listWidget = QtWidgets.QListWidget(GenericListDialog)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(GenericListDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(GenericListDialog)
        self.buttonBox.accepted.connect(GenericListDialog.accept)
        self.buttonBox.rejected.connect(GenericListDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GenericListDialog)

    def retranslateUi(self, GenericListDialog):
        _translate = QtCore.QCoreApplication.translate
        GenericListDialog.setWindowTitle(_translate("GenericListDialog", "Title"))
        self.label.setText(_translate("GenericListDialog", "Text"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    GenericListDialog = QtWidgets.QDialog()
    ui = Ui_GenericListDialog()
    ui.setupUi(GenericListDialog)
    GenericListDialog.show()
    sys.exit(app.exec_())
