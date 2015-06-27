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
        self.text.textChanged.connect(self.updateListFromData)
        self.text.returnPressed.connect(self.submit)
        self.listDelegate = listCompleterDelegate(self)
        self.list.setItemDelegate(self.listDelegate)
        self.list.itemActivated.connect(self.submit)
        
        self.outlineModel = mainWindow().mdlOutline
        self.persoModel = mainWindow().mdlPersos
        
        self.data = {}
        
        self.populate()
        self.hide()
        
    def popup(self, completion=""):
        self.text.setText(completion)
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
                    d.append((c.title(), c.ID(), c.path()))
                    addChildren(c)
            
            r = self.outlineModel.rootItem
            addChildren(r)
            
            self.data[(self.tr("Texts"), "T")] = d
            
        if self.persoModel:
            d = []
            
            for r in range(self.persoModel.rowCount()):
                name = self.persoModel.item(r, Perso.name.value).text()
                ID = self.persoModel.item(r, Perso.ID.value).text()
                imp = self.persoModel.item(r, Perso.importance.value).text()
                imp = [self.tr("Minor"), self.tr("Secondary"), self.tr("Main")][int(imp)]
                d.append((name, ID, imp))
            
            self.data[(self.tr("Characters"), "C")] = d
            
        self.updateListFromData()
            
    def updateListFromData(self):
        self.list.clear()
        for cat in self.data:
            filtered = [i for i in self.data[cat] if self.text.text().lower() in i[0].lower()]
            if filtered:
                self.addCategory(cat[0])
                for item in filtered:
                    i = QListWidgetItem(item[0])
                    i.setData(Qt.UserRole, "::{}:{}::".format(cat[1], item[1]))
                    i.setData(Qt.UserRole+1, item[2])
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
            
            
class listCompleterDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        
    def paint(self, painter, option, index):
        extra = index.data(Qt.UserRole+1)
        if not extra:
            return QStyledItemDelegate.paint(self, painter, option, index)
        
        else:
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.color(QPalette.Inactive, QPalette.Highlight))
 
            title = index.data()
            extra = " - {}".format(extra)
            painter.drawText(option.rect, Qt.AlignLeft, title)
            
            fm = QFontMetrics(option.font)
            w = fm.width(title)
            r = QRect(option.rect)
            r.setLeft(r.left() + w)
            painter.save()
            painter.setPen(Qt.gray)
            painter.drawText(r, Qt.AlignLeft, extra)
            painter.restore()