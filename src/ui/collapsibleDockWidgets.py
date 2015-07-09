#!/usr/bin/env python
#--!-- coding: utf8 --!--

from qt import *


class collapsibleDockWidgets(QToolBar):
    """
    QMainWindow "mixin" which provides auto-hiding support for dock widgets
    (not toolbars).
    """
    TRANSPOSED_AREA = {
        Qt.LeftDockWidgetArea: Qt.LeftToolBarArea,
        Qt.RightDockWidgetArea: Qt.RightToolBarArea,
        Qt.TopDockWidgetArea: Qt.TopToolBarArea,
        Qt.BottomDockWidgetArea: Qt.BottomToolBarArea,
        }

    def __init__(self, area, parent, name=""):
        QToolBar.__init__(self, parent)
        self._area = area
        if not name:
            name = self.tr("Dock Widgets Toolbar")
        self.setObjectName(name)
        self.setWindowTitle(name)

        self.setFloatable(False)
        self.setMovable(False)
        
        #self.setAllowedAreas(self.TRANSPOSED_AREA[self._area])
        self.parent().addToolBar(self.TRANSPOSED_AREA[self._area], self)
        
        # Dock widgets
        for d in self._dockWidgets():
            b = verticalButton(self)
            b.setDefaultAction(d.toggleViewAction())
            self.addWidget(b)
            
        self.addSeparator()
        
        # Other widgets
        self.otherWidgets = []
        self.currentGroup = None

    def _dockWidgets(self):
        mw = self.parent()
        for w in mw.findChildren(QDockWidget, None):
            yield w

    def addCustomWidget(self, text, widget, group=None):    
        a = QAction(text, self)
        a.setCheckable(True)
        a.setChecked(widget.isVisible())
        a.toggled.connect(widget.setVisible)
        #widget.installEventFilter(self)
        b = verticalButton(self)
        b.setDefaultAction(a)
        a2 = self.addWidget(b)
        self.otherWidgets.append((b, a2, widget, group))
        
    #def eventFilter(self, widget, event):
        #if event.type() in [QEvent.Show, QEvent.Hide]:
            #for btn, action, w, grp in self.otherWidgets:
                #if w == widget:
                    #btn.defaultAction().setChecked(event.type() == QEvent.Show)
        #return False
        
    def setCurrentGroup(self, group):
        self.currentGroup = group
        for btn, action, widget, grp in self.otherWidgets:
            if not grp == group or grp == None:
                action.setVisible(False)
            else:
                action.setVisible(True)
            

class verticalButton(QToolButton):
    def __init__(self, parent):
        QToolButton.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        
    def sizeHint(self):
        return QToolButton.sizeHint(self).transposed()
        
    def paintEvent(self, event):
        p = QStylePainter(self)
        p.rotate(90)
        p.translate(0, - self.width())
        opt = QStyleOptionButton()
        opt.initFrom(self)
        opt.text = self.text()
        if self.isChecked():
            opt.state |= QStyle.State_On
        s = opt.rect.size().transposed()
        opt.rect.setSize(s)
        p.drawControl(QStyle.CE_PushButton, opt)