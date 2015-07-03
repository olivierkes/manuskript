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
        ts = i.data(Qt.UserRole)
        item = self._index.internalPointer()
        
        textNow = item.text()
        textBefore = [r[1] for r in item.revisions() if r[0] == ts][0]
        
        textNow = textNow.splitlines()
        textBefore = textBefore.splitlines()
        
        d = difflib.Differ()
        diff = list(d.compare(textBefore, textNow))
        
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
            
            if op == "  ":
                if item.type() == "t2t":
                    txt = Ref.basicT2TFormat(txt)
                mydiff += "{}{}".format(txt, extra)
            elif op == "- " and op2 == "+ ":
                s = difflib.SequenceMatcher(None, txt, txt2, autojunk=False)
                for tag, i1, i2, j1, j2 in s.get_opcodes():
                    if tag == "equal":
                        mydiff += txt[i1:i2]
                    elif tag == "delete":
                        mydiff += "<span style='color:red;'>{}</span>".format(txt[i1:i2].replace(" ", "␣"))
                    elif tag == "insert":
                        mydiff += "<span style='color:green;'>{}</span>".format(txt2[j1:j2].replace(" ", "␣"))
                    elif tag == "replace":
                        mydiff += "<span style='color:red;'>{}</span>".format(txt[i1:i2].replace(" ", "␣"))
                        mydiff += "<span style='color:green;'>{}</span>".format(txt2[j1:j2].replace(" ", "␣"))
                mydiff += extra
                skip = True
            elif op == "- ":
                mydiff += "<span style='color:red;'>{}</span>{}".format(txt, extra)
            elif op == "+ ":
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