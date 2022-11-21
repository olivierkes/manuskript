from PyQt5.QtWidgets import QDialog
from manuskript.ui.listDialog_ui import Ui_GenericListDialog


class ListDialog(QDialog, Ui_GenericListDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

    def accept(self):
        self.hide()
        self.close()

    def reject(self):
        self.hide()
        self.close()
