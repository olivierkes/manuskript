#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from models.outlineModel import *
from ui.revisions_ui import *
from functions import *
import models.references as Ref
import datetime
import difflib

class revisions(QWidget, Ui_revisions):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.splitter.setStretchFactor(0, 5)
        self.splitter.setStretchFactor(1, 70)
        
        self.listDelegate = listCompleterDelegate(self)
        self.list.setItemDelegate(self.listDelegate)
        self.list.itemActivated.connect(self.showDiff)
        #self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.menu = QMenu(self)
        self.actGroup = QActionGroup(self)
        
        self.actShowDiff = QAction(self.tr("Show modifications"), self.menu)
        self.actShowDiff.setCheckable(True)
        self.actShowDiff.setChecked(True)
        self.actShowDiff.triggered.connect(self.showDiff)
        self.menu.addAction(self.actShowDiff)
        self.actGroup.addAction(self.actShowDiff)
        
        self.actShowVersion = QAction(self.tr("Show ancient version"), self.menu)
        self.actShowVersion.setCheckable(True)
        self.actShowVersion.setChecked(False)
        self.actShowVersion.triggered.connect(self.showDiff)
        self.menu.addAction(self.actShowVersion)
        self.actGroup.addAction(self.actShowVersion)
        
        self.menu.addSeparator()
        self.actShowSpaces = QAction(self.tr("Show spaces"), self.menu)
        self.actShowSpaces.setCheckable(True)
        self.actShowSpaces.setChecked(False)
        self.actShowSpaces.triggered.connect(self.showDiff)
        self.menu.addAction(self.actShowSpaces)
        
        self.actDiffOnly = QAction(self.tr("Show modifications only"), self.menu)
        self.actDiffOnly.setCheckable(True)
        self.actDiffOnly.setChecked(True)
        self.actDiffOnly.triggered.connect(self.showDiff)
        self.menu.addAction(self.actDiffOnly)
        self.btnOptions.setMenu(self.menu)
        
        self._model = None
        self._index = None
        
    def setModel(self, model):
        self._model = model
        self._model.dataChanged.connect(self.updateMaybe)
        
    def setCurrentModelIndex(self, index):
        self._index = index
        self.view.setText("")
        self.update()
        
    def updateMaybe(self, topLeft, bottomRight):
        if self._index and \
           topLeft.column() <= Outline.revisions.value <= bottomRight.column() and \
           topLeft.row() <= self._index.row() <= bottomRight.row():
            self.update()
            
    def update(self):
        self.list.clear()
        item = self._index.internalPointer()
        rev = item.revisions()
        # Sort revisions
        rev = sorted(rev, key=lambda x:x[0], reverse=True)
        for r in rev:
            timestamp = datetime.datetime.fromtimestamp(r[0]).strftime('%Y-%m-%d %H:%M:%S')
            readable = self.readableDelta(r[0])
            i = QListWidgetItem(readable)
            i.setData(Qt.UserRole, r[0])
            i.setData(Qt.UserRole+1, timestamp)
            self.list.addItem(i)
            
    def readableDelta(self, timestamp):
        now = datetime.datetime.now()
        delta = now - datetime.datetime.fromtimestamp(timestamp)
        if delta.days == 1:
            return self.tr("1 day ago")
        elif delta.days > 0:
            return self.tr("{} days ago").format(str(delta.days))
        elif delta.seconds > 60 * 60:
            return self.tr("{} hours ago").format(str(int(delta.seconds / 60 / 60)))
        elif delta.seconds > 60:
            return self.tr("{} minutes ago").format(str(int(delta.seconds / 60)))
        else:
            return self.tr("{} seconds ago").format(str(delta.seconds))
            
    def showDiff(self):
        #FIXME: doesn't work for HTML formatting.
        i = self.list.currentItem()
        
        if not i:
            return
        
        ts = i.data(Qt.UserRole)
        item = self._index.internalPointer()
        
        textNow = item.text()
        textBefore = [r[1] for r in item.revisions() if r[0] == ts][0]
        
        if self.actShowVersion.isChecked():
            if item.type() == "t2t":
                textBefore = Ref.basicT2TFormat(textBefore)
            self.view.setText(textBefore)
            return
        
        textNow = textNow.splitlines()
        textBefore = textBefore.splitlines()
        
        d = difflib.Differ()
        diff = list(d.compare(textBefore, textNow))
        
        if self.actShowSpaces.isChecked():
            _format = lambda x: x.replace(" ", "␣ ")
        else:
            _format = lambda x:x
        
        extra = "" if item.type() == "html" else "<br>"    
        diff = [d for d in diff if d and not d[:2] == "? "]
        mydiff = ""
        skip = False
        for n in range(len(diff)):
            l = diff[n]
            op = l[:2]
            txt = l[2:]
            op2 = diff[n+1][:2] if n+1 < len(diff) else None
            txt2 = diff[n+1][2:] if n+1 < len(diff) else None
            
            if skip:
                skip = False
                continue
            
            if op == "  " and not self.actDiffOnly.isChecked():
                if item.type() == "t2t":
                    txt = Ref.basicT2TFormat(txt)
                mydiff += "{}{}".format(txt, extra)
            elif op == "- " and op2 == "+ ":
                if self.actDiffOnly.isChecked():
                    mydiff += "<br>{}:<br>".format(str(n))
                s = difflib.SequenceMatcher(None, txt, txt2, autojunk=False)
                for tag, i1, i2, j1, j2 in s.get_opcodes():
                    if tag == "equal":
                        mydiff += txt[i1:i2]
                    elif tag == "delete":
                        mydiff += "<span style='color:red;'>{}</span>".format(_format(txt[i1:i2]))
                    elif tag == "insert":
                        mydiff += "<span style='color:green;'>{}</span>".format(_format(txt2[j1:j2]))
                    elif tag == "replace":
                        mydiff += "<span style='color:red;'>{}</span>".format(_format(txt[i1:i2]))
                        mydiff += "<span style='color:green;'>{}</span>".format(_format(txt2[j1:j2]))
                mydiff += extra
                skip = True
            elif op == "- ":
                if self.actDiffOnly.isChecked():
                    mydiff += "<br>{}:<br>".format(str(n))
                mydiff += "<span style='color:red;'>{}</span>{}".format(txt, extra)
            elif op == "+ ":
                if self.actDiffOnly.isChecked():
                    mydiff += "<br>{}:<br>".format(str(n))
                mydiff += "<span style='color:green;'>{}</span>{}".format(txt, extra)
        
        self.view.setText(mydiff)
        
            
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