#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from ui.views.textEditView import *
from ui.editors.themes import *
from functions import *
import settings

class fullScreenEditor(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._background = None
        self._theme = findThemePath(settings.fullScreenTheme)
        self._themeDatas = loadThemeDatas(self._theme)
        self.setMouseTracking(True)
        
        # Text editor
        self.editor = textEditView(self, dict=settings.dict)
        self.editor.setFrameStyle(QFrame.NoFrame)
        self.editor.document().setPlainText(open(appPath("resources/themes/preview.txt")).read() * 5)
        self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.editor.installEventFilter(self)
        self.editor.setMouseTracking(True)
        
        
        # Scroll bar
        if self._themeDatas["Foreground/Color"] == self._themeDatas["Background/Color"] or \
            self._themeDatas["Foreground/Opacity"] < 5:
                color = QColor(self._themeDatas["Text/Color"])
        else:
            color = QColor(self._themeDatas["Foreground/Color"])
            color.setAlpha(self._themeDatas["Foreground/Opacity"] * 255 / 100)
        self.editor.setVerticalScrollBar(myScrollBar(color))
        self.scrollBar = self.editor.verticalScrollBar()
        self.scrollBar.setParent(self)
        
        # Panel
        self.panel = myPanel(color, self)
        
        
        #self.updateTheme()
        self.showFullScreen()
        #self.showMaximized()
        #self.show()
        
    def setTheme(self, themeName):
        self._theme = findThemePath(settings.fullScreenTheme)
        self._themeDatas = loadThemeDatas(self._theme)
        self.updateTheme()
        
    def updateTheme(self):
        rect = self.geometry()
        self._background = generateTheme(self._themeDatas, rect)
        
        setThemeEditorDatas(self.editor, self._themeDatas, self._background, rect)
        
        #set ScrollBar
        r = self.editor.geometry()
        w = qApp.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        r.setWidth(w)
        r.moveRight(rect.right())
        self.scrollBar.setGeometry(r)
        self.scrollBar.setVisible(False)
        
        # Set Panel
        r = QRect(0, 0, 400, 120)
        r.moveBottom(rect.bottom())
        r.moveLeft(rect.center().x() - r.width() / 2)
        self.panel.setGeometry(r)
        self.panel.setVisible(False)
        
    def paintEvent(self, event):
        if self._background:
            painter = QPainter(self)
            painter.drawPixmap(event.rect(), self._background, event.rect())
            painter.end()
      
    def resizeEvent(self, event):
        self.updateTheme()
        
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Escape, Qt.Key_F11]:
            self.close()
        else:
            QWidget.keyPressEvent(self, event)
    
    def mouseMoveEvent(self, event):
        r = self.geometry()
        #print(event.pos(), r)
        
        for w in [self.scrollBar, self.panel]:
            w.setVisible(w.geometry().contains(event.pos()))    
            
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove or obj == self.editor and event.type() == QEvent.Enter:
            self.mouseMoveEvent(event)
        return QWidget.eventFilter(self, obj, event)
        
class myScrollBar(QScrollBar):
    def __init__(self, color=Qt.white, parent=None):
        QScrollBar.__init__(self, parent)
        self._color = color
        
    def paintEvent(self, event):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        style = qApp.style()
        painter = QPainter(self)
        #slider
        r = style.subControlRect(style.CC_ScrollBar, opt, style.SC_ScrollBarSlider)
        painter.fillRect(r, self._color)
        painter.end()
        
class myPanel(QWidget):
    def __init__(self, color=Qt.white, parent=None):
        QWidget.__init__(self, parent)
        self._color = color
        self.show()
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        r = event.rect()
        painter = QPainter(self)
        painter.fillRect(r, self._color)