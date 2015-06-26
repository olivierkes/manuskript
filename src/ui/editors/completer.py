#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from models.outlineModel import *
from ui.editors.completer_ui import *
from functions import *

class completer(QWidget, Ui_completer):
    
    activated = pyqtSignal(str)
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Popup)
        self.text.textEdited.connect(self.updateListFromData)
        self.text.returnPressed.connect(self.submit)
        self.list.itemActivated.connect(self.submit)
        
        self.outlineModel = mainWindow().mdlOutline
        self.persoModel = mainWindow().mdlPersos
        
        self.data = {}
        
        self.populate()
        self.hide()
        
    def popup(self):
        self.text.setFocus(Qt.PopupFocusReason)
        self.show()
        
    def addCategory(self, title):
        item = QListWidgetItem(title)
        item.setBackground(QBrush(lightBlue()))
        item.setForeground(QBrush(Qt.darkBlue))
        item.setFlags(Qt.ItemIsEnabled)
        self.list.addItem(item)
        
    def populate(self):
        if self.outlineModel:
            d = []
            
            def addChildren(item):
                for c in item.children():
                    d.append((c.title(), c.ID()))
                    addChildren(c)
            
            r = self.outlineModel.rootItem
            addChildren(r)
            
            self.data[(self.tr("Texts"), "T")] = d
            
        if self.persoModel:
            d = []
            
            for r in range(self.persoModel.rowCount()):
                name = self.persoModel.item(r, Perso.name.value).text()
                ID = self.persoModel.item(r, Perso.ID.value).text()
                d.append((name, ID))
            
            self.data[(self.tr("Characters"), "C")] = d
            
        self.updateListFromData()
            
    def updateListFromData(self):
        self.list.clear()
        for cat in self.data:
            self.addCategory(cat[0])
            for item in [i for i in self.data[cat] if self.text.text().lower() in i[0].lower()]:
                i = QListWidgetItem(item[0])
                i.setData(Qt.UserRole, "::{}:{}::".format(cat[1], item[1]))
                self.list.addItem(i)
        
        self.list.setCurrentRow(1)
        self.text.setFocus(Qt.PopupFocusReason)
        
    def submit(self):
        i = self.list.currentItem()
        self.activated.emit(i.data(Qt.UserRole))
        self.hide()
        
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Up, Qt.Key_Down]:
            self.list.keyPressEvent(event)
        else:
            QWidget.keyPressEvent(self, event)