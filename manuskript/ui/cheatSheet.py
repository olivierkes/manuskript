#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from models.outlineModel import *
from ui.cheatSheet_ui import *
from functions import *
import models.references as Ref

class cheatSheet(QWidget, Ui_cheatSheet):
    
    activated = pyqtSignal(str)
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.splitter.setStretchFactor(0, 5)
        self.splitter.setStretchFactor(1, 70)
        
        self.txtFilter.textChanged.connect(self.updateListFromData)
        self.txtFilter.returnPressed.connect(self.showInfos)
        self.listDelegate = listCompleterDelegate(self)
        self.list.setItemDelegate(self.listDelegate)
        self.list.itemActivated.connect(self.showInfos)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.linkActivated.connect(self.openLink)
        self.view.linkHovered.connect(self.linkHovered)
        
        self.outlineModel = None
        self.persoModel = None
        self.plotModel = None
        self.worldModel = None
        
        self.populateTimer = QTimer(self)
        self.populateTimer.setSingleShot(True)
        self.populateTimer.setInterval(500)
        self.populateTimer.timeout.connect(self.populate)
        self.populateTimer.stop()
        
        self.data = {}
        
        self.populate()
        
    def setModels(self):
        mw = mainWindow()
        self.outlineModel = mw.mdlOutline
        self.persoModel = mw.mdlPersos
        self.plotModel = mw.mdlPlots
        self.worldModel = mw.mdlWorld
        
        self.outlineModel.dataChanged.connect(self.populateTimer.start)
        self.persoModel.dataChanged.connect(self.populateTimer.start)
        self.plotModel.dataChanged.connect(self.populateTimer.start)
        self.worldModel.dataChanged.connect(self.populateTimer.start)
        
        self.populate()
        
    def populate(self):
        if self.persoModel:
            d = []
            
            for r in range(self.persoModel.rowCount()):
                name = self.persoModel.item(r, Perso.name.value).text()
                ID = self.persoModel.item(r, Perso.ID.value).text()
                imp = self.persoModel.item(r, Perso.importance.value).text()
                imp = [self.tr("Minor"), self.tr("Secondary"), self.tr("Main")][int(imp)]
                d.append((name, ID, imp))
            
            self.data[(self.tr("Characters"), Ref.PersoLetter)] = d
        
        if self.outlineModel:
            d = []
            
            def addChildren(item):
                for c in item.children():
                    d.append((c.title(), c.ID(), c.path()))
                    addChildren(c)
            
            r = self.outlineModel.rootItem
            addChildren(r)
            
            self.data[(self.tr("Texts"), Ref.TextLetter)] = d
            
        if self.plotModel:
            d = []
            
            for r in range(self.plotModel.rowCount()):
                name = self.plotModel.item(r, Plot.name.value).text()
                ID = self.plotModel.item(r, Plot.ID.value).text()
                imp = self.plotModel.item(r, Plot.importance.value).text()
                imp = [self.tr("Minor"), self.tr("Secondary"), self.tr("Main")][int(imp)]
                d.append((name, ID, imp))
            
            self.data[(self.tr("Plots"), Ref.PlotLetter)] = d
            
        if self.worldModel:
            d = self.worldModel.listAll()
            self.data[(self.tr("World"), Ref.WorldLetter)] = d
            
        self.updateListFromData()
            
    def addCategory(self, title):
        item = QListWidgetItem(title)
        item.setBackground(QBrush(lightBlue()))
        item.setForeground(QBrush(Qt.darkBlue))
        item.setFlags(Qt.ItemIsEnabled)
        f = item.font()
        f.setBold(True)
        item.setFont(f)
        self.list.addItem(item)
        
    def updateListFromData(self):
        self.list.clear()
        for cat in self.data:
            filtered = [i for i in self.data[cat] if self.txtFilter.text().lower() in i[0].lower()]
            if filtered:
                self.addCategory(cat[0])
                for item in filtered:
                    i = QListWidgetItem(item[0])
                    i.setData(Qt.UserRole, Ref.EmptyRef.format(cat[1], item[1], item[0]))
                    i.setData(Qt.UserRole+1, item[2])
                    self.list.addItem(i)
        
        self.list.setCurrentRow(1)
        
    def showInfos(self):
        i = self.list.currentItem()
        ref = i.data(Qt.UserRole)
        if ref:
            self.view.setText(Ref.infos(ref))
            
    def openLink(self, link):
        Ref.open(link)
        
    def linkHovered(self, link):
        if link:
            QToolTip.showText(QCursor.pos(), Ref.tooltip(link))
        
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