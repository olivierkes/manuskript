# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manuskript/ui/views/basicItemView_ui.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_basicItemView(object):
    def setupUi(self, basicItemView):
        basicItemView.setObjectName("basicItemView")
        basicItemView.resize(400, 425)
        self.verticalLayout = QtWidgets.QVBoxLayout(basicItemView)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem)
        self.lblPlanPOV = QtWidgets.QLabel(basicItemView)
        self.lblPlanPOV.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblPlanPOV.setObjectName("lblPlanPOV")
        self.horizontalLayout_11.addWidget(self.lblPlanPOV)
        self.cmbPOV = cmbOutlineCharacterChoser(basicItemView)
        self.cmbPOV.setFrame(False)
        self.cmbPOV.setObjectName("cmbPOV")
        self.horizontalLayout_11.addWidget(self.cmbPOV)
        self.lblGoal = QtWidgets.QLabel(basicItemView)
        self.lblGoal.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblGoal.setObjectName("lblGoal")
        self.horizontalLayout_11.addWidget(self.lblGoal)
        self.txtGoal = lineEditView(basicItemView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtGoal.sizePolicy().hasHeightForWidth())
        self.txtGoal.setSizePolicy(sizePolicy)
        self.txtGoal.setAutoFillBackground(False)
        self.txtGoal.setStyleSheet("border-radius: 6px;")
        self.txtGoal.setFrame(False)
        self.txtGoal.setObjectName("txtGoal")
        self.horizontalLayout_11.addWidget(self.txtGoal)
        self.verticalLayout.addLayout(self.horizontalLayout_11)
        self.txtSummarySentence = lineEditView(basicItemView)
        self.txtSummarySentence.setText("")
        self.txtSummarySentence.setObjectName("txtSummarySentence")
        self.verticalLayout.addWidget(self.txtSummarySentence)
        self.label_9 = QtWidgets.QLabel(basicItemView)
        self.label_9.setObjectName("label_9")
        self.verticalLayout.addWidget(self.label_9)
        self.txtSummaryFull = MDEditCompleter(basicItemView)
        self.txtSummaryFull.setObjectName("txtSummaryFull")
        self.verticalLayout.addWidget(self.txtSummaryFull)

        self.retranslateUi(basicItemView)
        QtCore.QMetaObject.connectSlotsByName(basicItemView)

    def retranslateUi(self, basicItemView):
        _translate = QtCore.QCoreApplication.translate
        basicItemView.setWindowTitle(_translate("basicItemView", "Form"))
        self.lblPlanPOV.setText(_translate("basicItemView", "POV:"))
        self.lblGoal.setText(_translate("basicItemView", "Goal:"))
        self.txtGoal.setPlaceholderText(_translate("basicItemView", "Word count"))
        self.txtSummarySentence.setPlaceholderText(_translate("basicItemView", "One line summary"))
        self.label_9.setText(_translate("basicItemView", "Few sentences summary:"))

from manuskript.ui.views.MDEditCompleter import MDEditCompleter
from manuskript.ui.views.cmbOutlineCharacterChoser import cmbOutlineCharacterChoser
from manuskript.ui.views.lineEditView import lineEditView
