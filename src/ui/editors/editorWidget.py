#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



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
        self.currentIndex = QModelIndex()
        self.txtEdits = []
        self.scroll.setBackgroundRole(QPalette.Base)
        self.toggledSpellcheck.connect(self.txtRedacText.toggleSpellcheck)
        self.dictChanged.connect(self.txtRedacText.setDict)
        self.currentDict = ""
        self.spellcheck = True
        self.folderView = "cork"
        
    def setModel(self, model):
        self._model = model
        self.setView()
        
    def setFolderView(self, v):
        oldV = self.folderView
        if v == "cork":
            self.folderView = "cork"
        elif v == "outline":
            self.folderView = "outline"
        else:
            self.folderView = "text"
            
        if oldV != self.folderView and self.currentIndex:
            self.setCurrentModelIndex(self.currentIndex)
        
    def setCorkSizeFactor(self, v):
        self.corkView.itemDelegate().setCorkSizeFactor(v)
        r = self.corkView.rootIndex()
        
        if r.isValid():
            count = r.internalPointer().childCount()
        else:
            count = self._model.rootItem.childCount()
        
        for c in range(count):
            self.corkView.itemDelegate().sizeHintChanged.emit(r.child(c, 0))
        
    def setView(self):
        index = mainWindow().treeRedacOutline.currentIndex()
        
        # Couting the number of other selected items
        sel = []
        for i in mainWindow().treeRedacOutline.selectionModel().selection().indexes():
            if i.column() != 0: continue
            if i not in sel: sel.append(i)
        
        if len(sel) != 0:
            item = index.internalPointer()
        else:
            index = QModelIndex()
            item = self._model.rootItem
            
        self.currentIndex = index
            
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
        
        def addSpacer():
            l.addItem(QSpacerItem(10, 1000, QSizePolicy.Minimum, QSizePolicy.Expanding))
            
        # Display multiple selected items
        if len(sel) > 1 and False:  # Buggy and not very useful, skip
            self.stack.setCurrentIndex(1)
            w = QWidget()
            l = QVBoxLayout(w)
            self.txtEdits = []
            for idx in sel:
                sItem = idx.internalPointer()
                addTitle(sItem)
                if sItem.isFolder():
                    addChildren(sItem)
                else:
                    addScene(sItem)
                addLine()
            addSpacer()
            self.scroll.setWidget(w)
            
        elif item.isFolder() and self.folderView == "text":
            self.stack.setCurrentIndex(1)
            
            w = QWidget()
            l = QVBoxLayout(w)
            #self.scroll.setWidgetResizable(False)
            
            self.txtEdits = []
            
            addTitle(item)
            addChildren(item)
            addSpacer()
            self.scroll.setWidget(w)
            
        elif item.isFolder() and self.folderView == "cork":
            self.stack.setCurrentIndex(2)
            self.corkView.setModel(self._model)
            self.corkView.setRootIndex(index)
            self.corkView.selectionModel().selectionChanged.connect(
                lambda: mainWindow().viewRedacProperties.selectionChanged(self.corkView))
            self.corkView.clicked.connect(
                lambda: mainWindow().viewRedacProperties.selectionChanged(self.corkView))
            
            
        elif item.isFolder() and self.folderView == "outline":
            self.stack.setCurrentIndex(3)
            self.outlineView.setModelPersos(mainWindow().mdlPersos)
            self.outlineView.setModelLabels(mainWindow().mdlLabels)
            self.outlineView.setModelStatus(mainWindow().mdlStatus)
            self.outlineView.setModel(self._model)
            self.outlineView.setRootIndex(index)
            self.outlineView.selectionModel().selectionChanged.connect(
                lambda: mainWindow().viewRedacProperties.selectionChanged(self.outlineView))
            self.outlineView.clicked.connect(
                lambda: mainWindow().viewRedacProperties.selectionChanged(self.outlineView))
            
            
        else:
            self.stack.setCurrentIndex(0)
        
        self._model.dataChanged.connect(self.modelDataChanged)
        self.updateStatusBar()
        
        
    def setCurrentModelIndex(self, index=None):
        if index.isValid():
            self.currentIndex = index
            self._model = index.model()
        else:
            self.currentIndex = QModelIndex()
            
        self.setView()
            
    def modelDataChanged(self, topLeft, bottomRight):
        if not self.currentIndex:
            return
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
                mw.lblRedacWC.setText(self.tr("{} words / {}").format(wc, goal))
            else:
                mw.lblRedacProgress.hide()
                mw.lblRedacWC.setText(self.tr("{} words").format(wc))
            
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
        
        self.stack.setStyleSheet("""
            QTextEdit {{
                margin-left: {m}px;
                margin-right: {m}px;
            }};""".format(
                m=str((qApp.desktop().screenGeometry(currentScreen).width() - 800) / 2))
            )
        
        self.move(qApp.desktop().screenGeometry(currentScreen).topLeft())
        QWidget.showFullScreen(self)
        
        #FIXME: too big?
        print(qApp.desktop().screenGeometry(currentScreen), self.geometry())
        
        
        
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