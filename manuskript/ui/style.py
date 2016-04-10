#!/usr/bin/env python
# --!-- coding: utf8 --!--


# default window color (linux):
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import qApp

window = "#d6d2d0" #"#eee"

bgHover = "#ccc"
bgChecked = "#bbb"
borderColor = "darkGray"

def mainWindowSS():
    return """
    QMenuBar#menubar{{border:none;}}

    QToolButton{{
        background: none;
        border: none;
    }}
    QPushButton:flat:hover, QToolButton:hover{{
        border: 1px solid {borderColor};
        border-radius: 3px;
        background: {bgHover};
    }}
    """.format(
        bgHover=bgHover,
        borderColor=borderColor
    )

def styleMainWindow(mw):
    mw.setStyleSheet(mainWindowSS())

    # Custon palette?
    qApp.setPalette(appPalette())

    mw.treeRedacOutline.setStyleSheet("""
            QTreeView{
                background: transparent;
                margin-top: 30px;
            }""")


def appPalette():
    p = qApp.palette()
    c = p.color(p.Window)
    # p.setColor(p.Window, QColor(window))
    # p.setColor(p.Base, c.lighter(115))
    # p.setColor(p.Base, QColor("#FFF"))
    return p


def collapsibleGroupBoxButton():
    s1 = """
        QPushButton{
            background-color: #BBB;
            border: none;
            padding: 2px;
        }
        QPushButton:checked, QPushButton:hover{
            font-style:italic;
            background-color:lightBlue;
        }"""

    s2 = """
        QPushButton{{
            background-color: transparent;
            border: none;
            border-top: 1px solid {bgChecked};
            padding: 4px 0px;
            font-weight: bold;
        }}
        QPushButton:hover{{
            background-color:{bgHover};
        }}
        """.format(
        bgHover=bgHover,
        bgChecked=bgChecked
    )

    return s2


def mainEditorTabSS():
    return """
        QTabWidget::pane{
            margin-top: -1px;
            border: 1px solid #999;
        }
        QTabWidget::tab-bar{
            left:25px;
        }
        QTabBar{
            background: transparent;
            border-radius: 0;
            border: 0px;
        }
        QTabBar::tab{
            margin: 2px 0 0 0;
            padding: 2px 9px;
            border: 1px solid #999;
            border-bottom: 0px;
            margin-top: 3px;
        }
        QTabBar::tab:selected{
            border: 1px solid #999;
            background: white;
            border-bottom: 0px;
            margin-top: 0px;
        }
        QTabBar::tab:!selected:hover{
            background:#ddd;
        }

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 10px;
}
QScrollBar::handle {
    background: rgba(180, 180, 180, 40%);
}
QScrollBar::add-line:vertical {
    width:0;
    height: 0;
    border: none;
    background: none;
}

QScrollBar::sub-line:vertical {
    width:0;
    height: 0;
    border: none;
    background: none;
}

        """

def toolBarSS():
    return """
        QToolBar{
            background:transparent;
            border: 0;
            border-left: 1px solid darkgray;
            spacing: 0px;
        }
        QToolBar:separator{
            border: none;
        }
        """

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
        borderColor=borderColor,
        bgChecked=bgChecked,
        bgHover=bgHover
    )


def dockSS():
    return """
            QDockWidget::title {
                text-align: left; /* align the text to the left */
                background: lightBlue;
                padding: 5px;
            }

            QDockWidget::close-button, QDockWidget::float-button {
                background: lightBlue;
            }
            """
