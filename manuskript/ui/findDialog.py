from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QHBoxLayout, QWidget

from inspect import signature

class FindDialog(QDialog):
    def __init__(self, parent, ew):   
        QDialog.__init__(self)
        self.setWindowTitle("Find Text")
        self.editorWindow = ew
        
        self.searchText = QLineEdit()
        
        self.findPrevButton = QPushButton("Find Previous")
        self.findPrevButton.clicked.connect(self.doFindPrev)

        self.findNextButton = QPushButton("Find Next")
        self.findNextButton.clicked.connect(self.doFindNext)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.searchText)
        self.layout.addWidget(self.findPrevButton)
        self.layout.addWidget(self.findNextButton)
        self.setLayout(self.layout)
        
        
    def doFindNext(self):
        # QTextDocument.FindFlags() creates a set of empty search flags
        self.editorWindow.find(self.searchText.text(), QTextDocument.FindFlags())
        
    def doFindPrev(self):
        self.editorWindow.find(self.searchText.text(), QTextDocument.FindBackward)
    
