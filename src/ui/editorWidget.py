#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *
from enums import *
from ui.editorWidget_ui import *

class GrowingTextEdit(QTextEdit):

    def __init__(self, index=None, html=None, parent=None):
        QTextEdit.__init__(self, parent)  
        self.document().contentsChanged.connect(self.sizeChange)
        
        self.heightMin = 0
        self.heightMax = 65000
        self.sizeChange()
        self.item = None
        
        if index:
            self.currentIndex = index
            self.item = index.internalPointer()
            self._model = index.model()
            
            self._model.dataChanged.connect(self.update)
            self.document().contentsChanged.connect(self.submit)
            
        else:
            self.document().setHtml(html)
            self.setReadOnly(True)
            
        self.updateText()
        
    def submit(self):
        self.item.setData(Outline.text.value, self.toPlainText())
        
    def update(self, topLeft, bottomRight):
        if topLeft.row() <= self.currentIndex.row() <= bottomRight.row():
            self.updateText()
            
    def updateText(self):
        if self.item:
            self.document().setPlainText(self.item.data(Outline.text.value))
        
    def resizeEvent(self, e):
        QTextEdit.resizeEvent(self, e)
        self.sizeChange()

    def sizeChange(self):
        docHeight = self.document().size().height()
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(docHeight)
    

class editorWidget(QWidget, Ui_editorWidget_ui):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.currentIndex = None
        self.txtEdits = []
        self.scroll.setBackgroundRole(QPalette.Base)
        
    def setCurrentModelIndex(self, index):
        
        if index.isValid():
            
            self.currentIndex = index
            self._model = index.model()
            
            item = index.internalPointer()
            
            if item.isFolder():
                self.stack.setCurrentIndex(1)
                
                w = QWidget()
                l = QVBoxLayout(w)
                #self.scroll.setWidgetResizable(False)
                
                self.txtEdits = []
                
                def addTitle(itm):
                    edt = GrowingTextEdit(html="<h{l}>{t}</h{l}>".format(l=min(itm.level()+1, 5), t=itm.title()))
                    edt.setFrameShape(QFrame.NoFrame)
                    self.txtEdits.append(edt)
                    l.addWidget(edt)
                
                def addLine():
                    line = QFrame(self.scene)
                    line.setFrameShape(QFrame.HLine)
                    line.setFrameShadow(QFrame.Sunken)
                    l.addWidget(line)
                
                def addScene(itm):
                    edt = GrowingTextEdit(index=itm.index())
                    edt.setFrameShape(QFrame.NoFrame)
                    edt.setStatusTip(itm.path())
                    #edt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    self.txtEdits.append(edt)
                    l.addWidget(edt)
                
                def addChildren(itm):
                
                    for c in range(itm.childCount()):
                        child = itm.child(c)
                        
                        if child.isFolder():
                            addTitle(child)
                            addChildren(child)
                            
                        else:
                            addScene(child)
                            addLine()
                
                addTitle(item)
                addChildren(item)
                l.addItem(QSpacerItem(10, 1000, QSizePolicy.Minimum, QSizePolicy.Expanding))
                self.scroll.setWidget(w)
                
                
            else:
                self.stack.setCurrentIndex(0)
            
        else:
            self.currentIndex = None
            