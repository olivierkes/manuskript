#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QToolBar, QDockWidget, QAction, QToolButton, QSizePolicy, QStylePainter, \
    QStyleOptionButton, QStyle

from manuskript.ui import style


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

        # self.setAllowedAreas(self.TRANSPOSED_AREA[self._area])
        self.parent().addToolBar(self.TRANSPOSED_AREA[self._area], self)

        self._dockToButtonAction = {}

        # Dock widgets
        for d in self._dockWidgets():
            b = verticalButton(self)
            b.setDefaultAction(d.toggleViewAction())
            # d.setStyleSheet("QDockWidget::title{background-color: red;}")
            # d.setTitleBarWidget(QLabel(d.windowTitle()))
            d.setStyleSheet(style.dockSS())
            a = self.addWidget(b)
            self._dockToButtonAction[d] = a

        self.addSeparator()

        # Other widgets
        self.otherWidgets = []
        self.currentGroup = None

        self.setStyleSheet(style.toolBarSS())

    def _dockWidgets(self):
        mw = self.parent()
        for w in mw.findChildren(QDockWidget, None):
            yield w

    def addCustomWidget(self, text, widget, group=None, defaultVisibility=True):
        """
        Adds a custom widget to the toolbar.
        
        `text` is the name that will displayed on the button to switch visibility.
        `widget` is the widget to control from the toolbar.
        `group` is an integer (or any hashable) if the current widget should not
            be displayed all the time. Call `collapsibleDockWidgets.setCurrentGroup`
            to switch to that group and hide other widgets.
        `defaultVisibility` is the default visibility of the item when it is added.
            This allows for the widget to be added to `collapsibleDockWidgets` after
            they've been created but before they are shown, and yet specify their
            desired visibility. Otherwise it creates troubes, see #167 on github:
            https://github.com/olivierkes/manuskript/issues/167.
        """
        a = QAction(text, self)
        a.setCheckable(True)
        a.setChecked(defaultVisibility)
        a.toggled.connect(widget.setVisible)
        widget.setVisible(defaultVisibility)
        # widget.installEventFilter(self)
        b = verticalButton(self)
        b.setDefaultAction(a)
        #b.setChecked(widget.isVisible())
        a2 = self.addWidget(b)
        self.otherWidgets.append((b, a2, widget, group))

        # def eventFilter(self, widget, event):
        # if event.type() in [QEvent.Show, QEvent.Hide]:
        # for btn, action, w, grp in self.otherWidgets:
        # if w == widget:
        # btn.defaultAction().setChecked(event.type() == QEvent.Show)
        # return False

    def setCurrentGroup(self, group):
        self.currentGroup = group
        for btn, action, widget, grp in self.otherWidgets:
            if not grp == group or grp is None:
                action.setVisible(False)
            else:
                action.setVisible(True)

    def setDockVisibility(self, dock, val):
        dock.setVisible(val)
        self._dockToButtonAction[dock].setVisible(val)

    def saveState(self):
        """
        Saves and returns the state of the custom widgets. The visibility of the
        docks is not saved since it is included in `QMainWindow.saveState`.
        """
        state = []
        for btn, act, w, grp in self.otherWidgets:
            state.append(
                (grp, btn.text(), btn.isChecked())
            )
        return state

    def restoreState(self, state):
        """Restores the state of the custom widgets."""
        for group, title, status in state:
            for btn, act, widget, grp in self.otherWidgets:
                # Strip '&' from both title and btn.text() to improve matching because
                #   title contains "&" shortcut character whereas btn.text() does not.
                if group == grp and title.replace('&', '') == btn.text().replace('&', ''):
                    btn.setChecked(status)
                    btn.defaultAction().setChecked(status)
                    widget.setVisible(status)


class verticalButton(QToolButton):
    def __init__(self, parent):
        QToolButton.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.setStyleSheet(style.verticalToolButtonSS())

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
