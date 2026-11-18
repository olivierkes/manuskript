from json import load
import PyQt5.QtCore as QtCore,PyQt5.QtGui as  QtGui, PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QWidget, QTreeWidget, QAbstractItemView, QHBoxLayout
from PyQt5.QtWidgets import QPushButton, QDialogButtonBox, QTreeWidgetItem
from PyQt5.QtCore import QRect, Qt, QSettings
from typing import Generator, overload, Any, Iterable, TYPE_CHECKING
from pathlib import Path
from atexit import register, unregister
type DATA = str | list[DATA] | dict[str, DATA]
if not TYPE_CHECKING:
    from PyQt5.QtWidgets import  QTreeWidgetItem as TreeWidgetItem
    class QTreeWidgetItem(TreeWidgetItem):
        def __hash__(self):
            return id(self)
WORLDBASE:dict[str, DATA]={
    "Fantasy world building":[
        {"Physical": [
                "Climate",
                "Topography",
                "Astronomy",
                "Natural resources",
                "Wild life",
                "Flora",
                "History",
                "Races",
                "Diseases"
                ]
            },
        {"Cultural": [
            "Customs",
            "Food",
            "Languages",
            "Education",
            "Dresses",
            "Science",
            "Calendar",
            "Bodily language",
            "Ethics",
            "Religion",
            "Government",
            "Politics",
            "Gender roles",
            "Music and arts",
            "Architecture",
            "Military",
            "Technology",
            "Courtship",
            "Demography",
            "Transportation",
            "Medicine"
        ]},
        {"Magic system": [
            "Rules",
            "Organization",
            "Magical objects",
            "Magical places",
            "Magical races"
        ]},
        "Important places",
        "Important objects"
        ],
    "Basic Kingdom":[
        {"Kingdom":[
            {"Physical": [
                "Climate",
                "Topography",
                "Astronomy",
                "Natural resources",
                "Wild life",
                "Flora",
                "History",
                "Races",
                "Diseases"
                ]},
            {"Cultural": [
                "Customs",
                "Food",
                "Languages",
                "Education",
                "Dresses",
                "Science",
                "Calendar",
                "Bodily language",
                "Ethics",
                "Religion",
                "Government",
                "Politics",
                "Gender roles",
                "Music and arts",
                "Architecture",
                "Military",
                "Technology",
                "Courtship",
                "Demography",
                "Transportation",
                "Medicine"
            ]},
            {"Magic system": [
                "Rules",
                "Organization",
                "Magical objects",
                "Magical places",
                "Magical races"
            ]},
            "Important places",
            "Important objects"
        ]
        }
    ]
}
TrStr=lambda t:QtCore.QCoreApplication.translate('Dialog', t)
WORLDBASE.update(QSettings().value('WORLDTEMPLATE', WORLDBASE))# probably a better, more specific place to save this 

@overload
def Translate(data:dict, enforce=True)->dict[str, DATA]:...
@overload
def Translate(data:str, enforce=True)->str:...
@overload
def Translate(data:list, enforce=True)->list[DATA]:...
@overload
def Translate(data:Any, enforce=True)-> DATA:...
def Translate(data:DATA, enforce=True)->str | DATA | dict[str, DATA]:
    if isinstance(data, str):
        return TrStr(data)
    elif isinstance(data, list):
        new:DATA=[]
        for item in data:
            new.append(Translate(item))
        return item
    elif isinstance(data, dict):
        new={}
        for key, item in data.items():
            new[TrStr(key)]=Translate(item)
        return new
    if enforce:
        raise ValueError(f'{data} is not a list or str or dict')
    return TrStr(data)

WORLDBASE:dict[str, DATA]=Translate(WORLDBASE, enforce=False)
class WorldTemplateTree(QTreeWidget):
    currentTree:'WorldTemplateTree|None'=None
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent) if parent is not None else  super().__init__()
        __class__.currentTree=self
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setWordWrap(True)
        self.setHeaderHidden(True)
        self.setObjectName("WorldTemplateTree")
        if h:=self.header():
            h.setCascadingSectionResizes(True)
        if (h2:=self.headerItem()):
            h2.setText(0, TrStr("Name"))
    def delI(self):
        def getParent(i):
            par = i.parent()
            if par is None:
                return self.invisibleRootItem()
            return par
        for i in self.selectedItems():
            if (par:=getParent(i)) is not None:
                par.removeChild(i)
                
    def add1(self):
        sel=self.selectedItems()
        if not sel:
            return
        parents:list[tuple[QTreeWidgetItem, int]]=[]
        for i in sel:
            par=i.parent() or self.invisibleRootItem()
            if par is None:
                continue
            parents.append((par,par.indexOfChild(i)))
        for p in parents:
            self.insertItem(parent=p[0], index=p[1], text='New Item')
    def addChild(self):
        sel=self.selectedItems()
        if not sel:
            return
        for p in sel:
            self.insertItem(parent=p,text='New Item')

    def insertItem(self, item:QTreeWidgetItem|None=None,parent:QTreeWidgetItem|None|object=None, index:int=-1, tosave=True, text:Any='', tr=True):
        """Insert or attach a tree item to the tree widget with text and check state."""
        if parent is None:
            parent=self.invisibleRootItem()
        if item is None:
            item=QTreeWidgetItem()
        if not isinstance(text, str) :
            text=str(text)
        if tr:
            text=TrStr(text)
        item.setText(0, text)
        item.setCheckState(0, Qt.CheckState.Unchecked if not tosave else Qt.CheckState.Checked)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        if parent is None:
            return item
        elif not isinstance(parent, QTreeWidgetItem):
            insertChild= self.insertTopLevelItem
            addChild=self.addTopLevelItem
        else:
            insertChild= parent.insertChild
            addChild=parent.addChild
        if index<0:
            addChild(item)
        else:
            insertChild(index, item)
        return item
    @classmethod
    def fromJson(cls, data:dict[str,DATA]=WORLDBASE, self:'WorldTemplateTree|None'=None):
        if self is None:
            self=cls()
        self.clear()
        def addItems(dat:DATA, item:QTreeWidgetItem):
            if isinstance(dat, dict):
                for key, d in dat.items():
                    addItems(d, self.insertItem(parent=item, text=key))
            elif isinstance(dat, list):
                for d in dat:
                    addItems(d, item)
            elif isinstance(dat, str):
                self.insertItem(parent=item, text=dat)
        i=self.invisibleRootItem() or object()
        # object() adds the item as toplevel
        for key, d in data.items():
            addItems(d, self.insertItem(parent=i, text=key))
        return self
    def toJson(self):
        def getChildValues(item, child_count):
            return {c:item_to_value(c, checkState(c)) for c in getChilds(item, child_count)}
        def checkState(item:QTreeWidgetItem):
            return item.checkState(0)== Qt.CheckState.Checked
        def getChilds(item, child_count) -> Generator[QTreeWidgetItem, None, None]:
            for i in range(child_count):
                i=item.child(i)
                if i is not None and checkState(item):
                    yield i
        def childcounts(item:QTreeWidgetItem, *child,child_count=None):
            children:Iterable[QTreeWidgetItem]
            if child:
                children=list(filter(lambda c:isinstance(c, QTreeWidgetItem), child))
            else:
                if child_count is None:
                    child_count=item.childCount()
                children=getChilds(item, child_count)
            return {childitem.childCount() for childitem in children}
        def toText(item)->str:
            return item.text(0)
        def item_to_value(item: QTreeWidgetItem, tosave=True)->'DATA|None':
            if not tosave:
                return
            child_count = item.childCount()
            # Leaf node
            if child_count == 0:
                return toText(item)
        
            children = getChildValues(item, child_count)
            child_counts=childcounts(item, *children.keys())
            if child_counts and 0 not in child_counts:
                # If every child is a parent, make a dict
                return {toText(c):value for c,value  in children.items() if value is not None}
            # If every child is a leaf (child_counts={0}), make a list 
            # Mixed children: list of DATA
            return [v for v in children.values() if v is not None]
        parent:dict[str, DATA]={}
        for item in self.topLevelItems():
            if (value:=item_to_value(item, checkState(item))) is not None:
                parent[toText(item)]=value
        return parent
    def topLevelItems(self):
        for i in range(self.topLevelItemCount()):
            if (item:=self.topLevelItem(i)) is not None:
                yield item
            else:
                break
Tree=None
def getTree():
    global Tree
    if Tree is  None:
        WorldTemplateTree.currentTree=Tree=WorldTemplateTree.fromJson(WORLDBASE)
    return Tree

class WorldTemplateDialog(QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__()if parent is None  else super().__init__(parent)
        self.setupUi()
    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(400, 300)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.ScrollContents = QWidget()
        self.ScrollContents.setGeometry(QRect(0, 0, 386, 265))
        self.ScrollContents.setObjectName("ScrollContents")
        self.ScrollVLayout = QVBoxLayout(self.ScrollContents)
        self.ScrollVLayout.setObjectName("ScrollVLayout")
        self.WorldTemplateTree = getTree()#WorldTemplateTree(self.ScrollContents)
        self.ScrollVLayout.addWidget(self.WorldTemplateTree)
        self.BtnHLayout = QHBoxLayout()
        self.BtnHLayout.setObjectName("BtnHLayout")
        self.AddBtn = QPushButton(self.ScrollContents)
        self.AddBtn.setObjectName("AddBtn")
        self.BtnHLayout.addWidget(self.AddBtn)
        self.AddChildBtn = QPushButton(self.ScrollContents)
        self.AddChildBtn.setObjectName("AddChildBtn")
        self.BtnHLayout.addWidget(self.AddChildBtn)
        self.DelBtn = QPushButton(self.ScrollContents)
        self.DelBtn.setObjectName("DelBtn")
        self.BtnHLayout.addWidget(self.DelBtn)
        self.ScrollVLayout.addLayout(self.BtnHLayout)
        self.scrollArea.setWidget(self.ScrollContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.buttonBox = QDialogButtonBox(self)

        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok|QDialogButtonBox.Save)
        if b:=self.buttonBox.button(QDialogButtonBox.Ok):
            b.setToolTip('Only changes Worldbase for this session, but note that if Save is later called, it might be saved')
        if b:=self.buttonBox.button(QDialogButtonBox.Save):
            b.setToolTip('Save will save our current template to manuskript/models/Wmodels/world.json, so it can be reused on the next loading')
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.retranslateUi()
        self.buttonBox.accepted.connect(self.accept) 
        self.buttonBox.rejected.connect(self.reject) 
        saveBtn=self.buttonBox.button(QDialogButtonBox.StandardButton.Save)
        if saveBtn:
            saveBtn.clicked.connect(self.save)
        register(self.save)
        self.DelBtn.clicked.connect(self.WorldTemplateTree.delI)
        self.AddBtn.clicked.connect(self.WorldTemplateTree.add1)
        self.AddChildBtn.clicked.connect(self.WorldTemplateTree.addChild)
    def __del__(self, *a,**k):
        unregister(self.save)
    def exec(self) -> int:
        try:
            return super().exec()
        finally:
            self.detachTree('exec')
            unregister(self.save)
    def close(self) -> bool:
        try:
            return super().close()
        finally:
            self.detachTree('close')
    def detachTree(self, con=''):
        self.ScrollVLayout.removeWidget(self.WorldTemplateTree)
        self.WorldTemplateTree.setParent(None)
        unregister(self.save)
    def closeEvent(self, a0: QtGui.QCloseEvent | None) -> None:
        self.detachTree('closeevent')
        return super().closeEvent(a0)
    def exec_(self) -> int:
        try:
            return super().exec_()
        finally:
            self.detachTree('exec_')
        
    @staticmethod
    def trans(t):
        return QtCore.QCoreApplication.translate('Dialog', t)

    def save(self,*args):
        data=self.toJson()
        QSettings().setValue('WORLDTEMPLATE', data)
        return data
            
    @classmethod
    def fromJson(cls, data:dict[str,DATA]=WORLDBASE, self:'WorldTemplateDialog|None'=None):
        if self is None:
            self=cls()
        self.WorldTemplateTree=WorldTemplateTree.fromJson(data)
        return self
    def toJson(self):            
        return self.WorldTemplateTree.toJson()
    def retranslateUi(self):
        self.setWindowTitle(self.trans("Dialog"))    
        self.AddBtn.setText(self.trans("Add"))
        self.AddChildBtn.setText(self.trans("Add Child"))
        self.DelBtn.setText(self.trans("Delete"))
    @classmethod
    def new(cls):
        return cls().exec()