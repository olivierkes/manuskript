#!/usr/bin/env python
# --!-- coding: utf8 --!--


# default window color (linux):
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import qApp

from manuskript import settings
from manuskript import functions as F

# Loading palette colors.
# Manuskript as to restart to reload
p = qApp.palette()
# window = "#d6d2d0" #"#eee" / #eff0f1
window = p.color(QPalette.Window).name()            # General background
windowText = p.color(QPalette.WindowText).name()    # General foregroung
base = p.color(QPalette.Base).name()                # Other background
alternateBase = p.color(QPalette.AlternateBase).name() # Other background
text = p.color(QPalette.Text).name()                # Base Text
brightText = p.color(QPalette.BrightText).name()    # Contrast Text
button = p.color(QPalette.Button).name()            # Button background
buttonText = p.color(QPalette.ButtonText).name()    # Button Text
highlight = p.color(QPalette.Highlight).name()      # Other background
highlightedText = p.color(QPalette.HighlightedText).name() # Base Text

light = p.color(QPalette.Light).name()       # Lighter than Button color
midlight = p.color(QPalette.Midlight).name() # Between Button and Light
dark = p.color(QPalette.Dark).name()         # Darker than Button
mid = p.color(QPalette.Mid).name()           # Between Button and Dark
shadow = p.color(QPalette.Shadow).name()     # A very dark color

highlightLight = F.mixColors(highlight, window, .3)
highlightedTextDark = F.mixColors(highlight, text, .3)
highlightedTextLight = F.mixColors(highlight, highlightedText)
midlighter = F.mixColors(mid, window, .4)
textLight = F.mixColors(window, text)


#from manuskript.ui import style as S
#QColor(S.highlightedTextDark)
#QColor(S.highlightLight)


def mainWindowSS():
    return """
    QMenuBar#menubar{{border:none;}}

    QToolButton{{
        background: none;
        border: none;
    }}
    QPushButton:flat:hover, QToolButton:hover{{
        border: 1px solid {borderHover};
        border-radius: 3px;
        background: {backgroundHover};
    }}
    """.format(
        backgroundHover=highlightLight,
        borderHover=mid
    )

def styleMainWindow(mw):
    mw.setStyleSheet(mainWindowSS())
    mw.lstTabs.verticalScrollBar().setStyleSheet(simpleScrollBarV())

    # Custon palette?
    #qApp.setPalette(appPalette())

    mw.treeRedacOutline.setStyleSheet("""
            QTreeView{
                background: transparent;
                margin-top: 30px;
            }""" + simpleScrollBarV())

    mw.lstTabs.setStyleSheet("""
        QListView {{
            show-decoration-selected: 0;
            outline: none;
            background-color: transparent;
        }}

        QListView::item:selected {{
            background: {highlight};
            color: {textSelected}
        }}

        QListView::item:hover {{
            background: {hover};
        }}
        """.format(
            hover=highlight,
            highlight=highlightLight,
            textSelected=text,
        ))


def appPalette():
    p = qApp.palette()
    c = p.color(p.Window)
    # p.setColor(p.Window, QColor(window))
    # p.setColor(p.Base, c.lighter(115))
    # p.setColor(p.Base, QColor("#FFF"))
    return p

    # dark_palette = QPalette()
    # dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.WindowText, Qt.white)
    # dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    # dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    # dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    # dark_palette.setColor(QPalette.Text, Qt.white)
    # dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.ButtonText, Qt.white)
    # dark_palette.setColor(QPalette.BrightText, Qt.red)
    # dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    # dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    # dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    # qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    #
    # return dark_palette


def collapsibleGroupBoxButton():
    s1 = """
        QPushButton{{
            background-color: #BBB;
            border: none;
            padding: 2px;
        }}
        QPushButton:checked, QPushButton:hover{{
            font-style:italic;
            background-color:{bg};
        }}""".format(bg=highlightLight)

    s2 = """
        QPushButton{{
            background-color: transparent;
            border: none;
            border-top: 1px solid {border};
            padding: 4px 0px;
            font-weight: bold;
        }}
        QPushButton:hover{{
            background-color:{hover};
        }}
        """.format(
        hover=highlightLight,
        border=mid,
    )

    return s2


def mainEditorTabSS():
    if not settings.textEditor["backgroundTransparent"]:
        SS = """
            QTabWidget::pane{{
                margin-top: -1px;
                border: 1px solid {borderColor};
            }}
            QTabWidget::tab-bar{{
                left:50px;
            }}
            QTabBar{{
                background: transparent;
                border-radius: 0;
                border: 0px;
            }}
            QTabBar::tab{{
                padding: 2px 9px;
                border: 1px solid {borderColor};
                border-bottom: 0px;
            }}
            QTabBar::tab:selected{{
                border: 1px solid {borderColor};
                background: {bgColor};
                border-bottom: 0px;
                color: {foreground};
            }}
            QTabBar::tab:!selected:hover{{
                background:{highlight};
                color: {highlightedText};
            }}
            """.format(
                bgColor=settings.textEditor["background"],
                foreground=settings.textEditor["fontColor"],
                borderColor=mid,
                highlight=highlight,
                highlightedText=highlightedText,
            )
    else:
        # Transparent text view
        SS = """
            QTabWidget::pane{{
                margin-top: -1px;
                border: none;
            }}
            QTabWidget::tab-bar{{
                left:50px;
            }}
            QTabBar{{
                background: transparent;
                border: 0px;
            }}
            QTabBar::tab{{
                padding: 2px 9px;
                border: 1px solid {borderColor};
            }}
            QTabBar::tab:selected{{
                border: 1px solid {borderColor};
                background: {highlight};
                color: {highlightedText};
            }}
            QTabBar::tab:!selected:hover{{
                background:{highlight};
                color: {highlightedText};
            }}
            """.format(
                highlight=highlight,
                highlightedText=highlightedText,
                text=text,
                borderColor=mid,
            )

    # Add scrollbar
    SS += simpleScrollBarV(handle=mid, width=10)

    return SS


def toolBarSS():
    return """
        QToolBar{{
            background:transparent;
            border: 0;
            border-left: 1px solid {border};
            spacing: 0px;
        }}
        QToolBar:separator{{
            border: none;
        }}
        """.format(
            border=midlighter,
            )

def verticalToolButtonSS():
    return """
        QToolButton{{
            border: none;
            border-radius: 0px;
            background: transparent;
            margin: 0px;
            padding: 4px 8px;
        }}
        QToolButton:checked{{
            border: 0px solid {borderColor};
            background: {bgChecked};
        }}
        QToolButton:hover{{
            border: 0px solid {borderColor};
            background: {bgHover};
        }}
        """.format(
        borderColor=mid,
        bgChecked=midlighter,
        bgHover=highlightLight,
    )


def dockSS():

    return """
        QDockWidget::title {{
            text-align: left; /* align the text to the left */
            background: {header};
            padding: 5px;
        }}

        QDockWidget::close-button, QDockWidget::float-button {{
            background: {header};
        }}
        """.format(
        header=highlightLight,
        button=button
    )


def searchResultSS():
    return """
        QListWidget{{
            background: {window};
        }}
        """.format(
        window=window
    )


def lineEditSS():
    # return "border-radius: 6px;"
    return """QLineEdit{{
        border: none;
        border-bottom: 1px solid {line};
        background:{window};
    }}
    QLineEdit:focus{{
        border-bottom: 1px solid {highlight};
    }}
    """.format(window=window,
               line=mid,
               highlight=highlight)


def transparentSS():
    return """
        QTextEdit{
            background: transparent;
            border:none;
        }"""

def simpleScrollBarV(handle=None, width=8):
    # system default is (i think): mid background, dark handle

    default = midlighter

    handle = handle or default
    return """
        QScrollBar:vertical {{
            border: none;
            background: {background};
            width: {width}px;
        }}
        QScrollBar::handle {{
            background: {handle};
        }}
        QScrollBar::add-line:vertical {{
            width:0;
            height: 0;
            border: none;
            background: none;
        }}

        QScrollBar::sub-line:vertical {{
            width:0;
            height: 0;
            border: none;
            background: none;
        }}""".format(
            background="transparent",
            handle=handle,
            width=width)

def toolBoxSS():
    return """
    QToolBox::tab{{
        background-color: {background};
        padding: 2px;
        border: none;
    }}

    QToolBox::tab:selected, QToolBox::tab:hover{{
        background-color:{backgroundHover};
        color: {colorHover};
    }}""".format(
            background=highlightLight,
            backgroundHover=highlight,
            colorHover=highlightedText,
        )

def titleLabelSS():
    return """
        QLabel{{
            background-color:{bg};
            border:none;
            padding:10px;
            color:{text};
            font-size:16px;
            font-weight:bold;
            text-align:center;
        }}""".format(
            bg=highlightLight,
            text=highlightedTextDark,
            )
