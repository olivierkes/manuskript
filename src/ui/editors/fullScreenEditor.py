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
        f = QFile(appPath("resources/themes/preview.txt"))
        f.open(QIODevice.ReadOnly)
        self.editor.setPlainText(QTextStream(f).readAll()*5)
        self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.editor.installEventFilter(self)
        self.editor.setMouseTracking(True)
        
        self.editor.setVerticalScrollBar(myScrollBar())
        self.scrollBar = self.editor.verticalScrollBar()
        self.scrollBar.setParent(self)
        
        # Panel
        self.topPanel = myPanel(parent=self)
        self.bottomPanel = myPanel(parent=self)
        
        b = QPushButton(self)
        b.setIcon(qApp.style().standardIcon(QStyle.SP_DialogCloseButton))
        b.clicked.connect(self.close)
        b.setFlat(True)
        self.topPanel.layout().insertWidget(1, b)
        
        self.lstThemes = QComboBox(self)
        self.lstThemes.setAttribute(Qt.WA_TranslucentBackground)
        self.bottomPanel.layout().addWidget(self.lstThemes)
        
        paths = allPaths("resources/themes")
        
        for p in paths:
            lst = [i for i in os.listdir(p) if os.path.splitext(i)[1] == ".theme"]
            for t in lst:
                themeIni = os.path.join(p, t)
                self.lstThemes.addItem(os.path.splitext(t)[0])
        
        self.lstThemes.currentTextChanged.connect(self.setTheme)
        
        #self.updateTheme()
        self.showFullScreen()
        #self.showMaximized()
        #self.show()
        
    def setTheme(self, themeName):
        self._theme = findThemePath(themeName)
        self._themeDatas = loadThemeDatas(self._theme)
        self.updateTheme()
        
    def updateTheme(self):
        rect = self.geometry()
        self._background = generateTheme(self._themeDatas, rect)
        
        setThemeEditorDatas(self.editor, self._themeDatas, self._background, rect)
        
        # Colors
        if self._themeDatas["Foreground/Color"] == self._themeDatas["Background/Color"] or \
            self._themeDatas["Foreground/Opacity"] < 5:
                self._bgcolor = QColor(self._themeDatas["Text/Color"])
                self._fgcolor = QColor(self._themeDatas["Background/Color"])
        else:
            self._bgcolor = QColor(self._themeDatas["Foreground/Color"])
            self._bgcolor.setAlpha(self._themeDatas["Foreground/Opacity"] * 255 / 100)
            self._fgcolor = QColor(self._themeDatas["Text/Color"])
            
        # ScrollBar
        r = self.editor.geometry()
        w = qApp.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        r.setWidth(w)
        r.moveRight(rect.right())
        self.scrollBar.setGeometry(r)
        self.scrollBar.setVisible(False)
        p = self.scrollBar.palette()
        b = QBrush(self._background.copy(self.scrollBar.geometry()))
        p.setBrush(QPalette.Base, b)
        self.scrollBar.setPalette(p)
        
        self.scrollBar.setColor(self._bgcolor)
        
        # Panels
        r = QRect(0, 0, 0, 24)
        r.setWidth(rect.width())
        r.moveLeft(rect.center().x() - r.width() / 2)
        self.topPanel.setGeometry(r)
        self.topPanel.setVisible(False)
        r.moveBottom(rect.bottom())
        self.bottomPanel.setGeometry(r)
        self.bottomPanel.setVisible(False)
        self.topPanel.setColor(self._bgcolor)
        self.bottomPanel.setColor(self._bgcolor)
        
        # Lst theme
        p = self.lstThemes.palette()
        p.setBrush(QPalette.Button, self._bgcolor)
        p.setBrush(QPalette.ButtonText, self._fgcolor)
        p.setBrush(QPalette.WindowText, self._fgcolor)
        self.lstThemes.setPalette(p)
        
        self.update()
        
    def paintEvent(self, event):
        if self._background:
            painter = QPainter(self)
            painter.setClipRegion(event.region())
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
        
        for w in [self.scrollBar, self.topPanel, self.bottomPanel]:
            w.setVisible(w.geometry().contains(event.pos()))    
            
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove or obj == self.editor and event.type() == QEvent.Enter:
            self.mouseMoveEvent(event)
        return QWidget.eventFilter(self, obj, event)
        
class myScrollBar(QScrollBar):
    def __init__(self, color=Qt.white, parent=None):
        QScrollBar.__init__(self, parent)
        self._color = color
        #self.setAttribute(Qt.WA_TranslucentBackground)
        self.timer = QTimer()
        self.timer.setInterval(250)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)
        self.valueChanged.connect(lambda v: self.timer.start())
        self.valueChanged.connect(self.show)
        
    def setColor(self, color):
        self._color = color
        
    def paintEvent(self, event):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        style = qApp.style()
        painter = QPainter(self)
        
        # Background (Necessary with Qt 5.2 it seems, not with 5.4)
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.palette().brush(QPalette.Base))
        painter.drawRect(event.rect())
        painter.restore()
        
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
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addStretch(1)
        
    def setColor(self, color):
        self._color = color
        
    def paintEvent(self, event):
        r = event.rect()
        painter = QPainter(self)
        painter.fillRect(r, self._color)