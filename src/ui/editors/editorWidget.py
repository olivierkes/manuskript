#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *
from enums import *
from ui.editors.editorWidget_ui import *
from ui.editors.customTextEdit import *
from functions import *

class editorWidget(QWidget, Ui_editorWidget_ui):
    
    toggledSpellcheck = pyqtSignal(bool)
    dictChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.currentIndex = None
        self.txtEdits = []
        self.scroll.setBackgroundRole(QPalette.Base)
        self.toggledSpellcheck.connect(self.txtRedacText.toggleSpellcheck)
        self.dictChanged.connect(self.txtRedacText.setDict)
        self.currentDict = ""
        self.spellcheck = True
        
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
                    edt = customTextEdit(self, html="<h{l}>{t}</h{l}>".format(l=min(itm.level()+1, 5), t=itm.title()), autoResize=True)
                    edt.setFrameShape(QFrame.NoFrame)
                    self.txtEdits.append(edt)
                    l.addWidget(edt)
                
                def addLine():
                    line = QFrame(self.scene)
                    line.setFrameShape(QFrame.HLine)
                    line.setFrameShadow(QFrame.Sunken)
                    l.addWidget(line)
                
                def addScene(itm):
                    edt = customTextEdit(self, index=itm.index(), spellcheck=self.spellcheck, dict=self.currentDict, autoResize=True)
                    edt.setFrameShape(QFrame.NoFrame)
                    edt.setStatusTip(itm.path())
                    self.toggledSpellcheck.connect(edt.toggleSpellcheck)
                    self.dictChanged.connect(edt.setDict)
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
            
            self._model.dataChanged.connect(self.modelDataChanged)
            self.updateStatusBar()
            
        else:
            self.currentIndex = None
            
    def modelDataChanged(self, topLeft, bottomRight):
        if topLeft.row() <= self.currentIndex.row() <= bottomRight.row():
            self.updateStatusBar()
            
    def updateStatusBar(self):
        # Update progress
        if self.currentIndex and self.currentIndex.isValid():
            item = self.currentIndex.internalPointer()
            
            wc = item.data(Outline.wordCount.value)
            goal = item.data(Outline.goal.value)
            pg = item.data(Outline.goalPercentage.value)
            #mw = qApp.activeWindow()
            
            mw = mainWindow()
            
            if not mw: return
            
            if goal:
                mw.lblRedacProgress.show()
                rect = mw.lblRedacProgress.geometry()
                rect = QRect(QPoint(0, 0), rect.size())
                self.px = QPixmap(rect.size())
                self.px.fill(Qt.transparent)
                p = QPainter(self.px)
                drawProgress(p, rect, pg, 2)
                del p
                mw.lblRedacProgress.setPixmap(self.px)
                mw.lblRedacWC.setText("{} mots / {}".format(wc, goal))
            else:
                mw.lblRedacProgress.hide()
                mw.lblRedacWC.setText("{} mots".format(wc))
            
    def toggleSpellcheck(self, v):
        self.spellcheck = v
        self.toggledSpellcheck.emit(v)
        
    def setDict(self, dct):
        self.currentDict = dct
        self.dictChanged.emit(dct)
        
    def showFullscreen(self):
        self._parent = self.parent()
        self._geometry = self.geometry()
        self._fullscreen = True
        currentScreen = qApp.desktop().screenNumber(self)
        self.setParent(None)
        mainWindow().hide()
        self.move(qApp.desktop().screenGeometry(currentScreen).topLeft())
        
        self.stack.setStyleSheet("""
            QTextEdit {{
                margin-left: {m}px;
                margin-right: {m}px;
            }};""".format(
                m=str((qApp.desktop().screenGeometry(currentScreen).width() - 800) / 2))
            )
        
        QWidget.showFullScreen(self)
        
        
        
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Escape, Qt.Key_F11] and self._fullscreen:
            mainWindow().show()
            self.stack.setStyleSheet("")
            self.setGeometry(self._geometry)
            self.setParent(self._parent)
            self._parent.layout().insertWidget(1, self)
            self._fullscreen = False
        else:
            QWidget.keyPressEvent(self, event)