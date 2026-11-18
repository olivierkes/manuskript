#!/usr/bin/env python
# --!-- coding: utf8 --!--


# default window color (linux):
from PyQt5.QtWidgets import qApp
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from manuskript import settings
from manuskript import functions as F
from manuskript.ui.CSS import get as getStyleSheet, css_to_dict, strformat
# Loading palette colors.
# Manuskript as to restart to reload
p = qApp.palette()
# window = "#d6d2d0" #"#eee" / #eff0f1
window = p.color(QPalette.Window).name()            # General background
windowText = p.color(QPalette.WindowText).name()    # General foreground
base = p.color(QPalette.Base).name()                # Other background
alternateBase = p.color(QPalette.AlternateBase).name() # Other background
text = p.color(QPalette.Text).name()                # Base Text
brightText = p.color(QPalette.BrightText).name()    # Contrast Text
button = p.color(QPalette.Button).name()            # Button background
buttonText = p.color(QPalette.ButtonText).name()    # Button Text
highlight = p.color(QPalette.Highlight).name()      # Other background
highlightedText = p.color(QPalette.HighlightedText).name() # Base Text
link = p.color(QPalette.Link).name()                # Link
linkVisited = p.color(QPalette.LinkVisited).name()  # Link visited

light = p.color(QPalette.Light).name()       # Lighter than Button color
midlight = p.color(QPalette.Midlight).name() # Between Button and Light
mid = p.color(QPalette.Mid).name()           # Between Button and Dark
dark = p.color(QPalette.Dark).name()         # Darker than Button
shadow = p.color(QPalette.Shadow).name()     # A very dark color

highlightLight = F.mixColors(highlight, window, .3)
highlightedTextDark = F.mixColors(highlight, text, .3)
highlightedTextLight = F.mixColors(highlight, highlightedText)
midlighter = F.mixColors(mid, window, .4)
textLight = F.mixColors(window, text)
textLighter = F.mixColors(window, text, .85)

colors={
    'window':window,
    'windowText':windowText,
    'base':base,
    'alternateBase':alternateBase,
    'text':text,
    'brightText':brightText,
    'button':button,
    'buttonText':buttonText,
    'highlight':highlight,
    'highlightedText':highlightedText,
    'link':link,
    'linkVisited':linkVisited,
    'light':light,
    'midlight':midlight,
    'mid':mid,
    'dark':dark,
    'shadow':shadow,
    'highlightLight':highlightLight,
    'highlightedTextDark':highlightedTextDark,
    'highlightedTextLight':highlightedTextLight,
    'midlighter':midlighter,
    'textLight':textLight,
    'textLighter':textLighter,
}
#from manuskript.ui import style as S
#QColor(S.highlightedTextDark)
#QColor(S.highlightLight)
minor= getStyleSheet('minorSS').format(header=highlightLight, button=button, window=window, line=mid, highlight=highlight, bg=highlightLight,text=highlightedTextDark)
minordict=css_to_dict(minor)

def mainWindowSS():
    return getStyleSheet('mainWindowSS').format(backgroundHover=highlightLight, borderHover=mid, mid=mid, highlightLight=highlightLight)
def styleMainWindow(mw):
    mw.setStyleSheet(mainWindowSS())
    mw.lstTabs.verticalScrollBar().setStyleSheet(simpleScrollBarV())
    # Custom palette?
    #qApp.setPalette(appPalette())
    mw.treeRedacOutline.setStyleSheet(getStyleSheet('QTreeView') + simpleScrollBarV())
    mw.lstTabs.setStyleSheet(getStyleSheet('QListView').format(hover=highlight,highlight=highlightLight,textSelected=text))
def appPalette(setcolors=False):
    p = qApp.palette()
    if setcolors:
        c = p.color(p.Window)
        p.setColor(p.Window, QColor(window))
        p.setColor(p.Base, c.lighter(115))
        p.setColor(p.Base, QColor("#FFF"))
    return p
def getdark_palette(setQToolTip=False, dark_palette:None|QPalette=None):
    if not isinstance(dark_palette, QPalette):
        dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.GlobalColor.black)
    if setQToolTip:
        qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    return dark_palette


def collapsibleGroupBoxButton():
    s1 =getStyleSheet('collapsibleGroupBoxButtonv1').format(bg=highlightLight)
    s2 =getStyleSheet('collapsibleGroupBoxButtonv2', s1).format(hover=highlightLight,border=mid)
    return s2


def mainEditorTabSS():
    if not settings.textEditor["backgroundTransparent"]:
        SS =getStyleSheet('mainEditorTabSS').format(
                bgColor=textLighter,
                bgColorSelected=settings.textEditor["background"],
                foreground=settings.textEditor["fontColor"],
                borderColor=mid,
                highlight=highlight,
                highlightedText=highlightedText,
                bw=0,
            )
    else:
        SS=getStyleSheet('mainEditorTabSSTransparent').format(
                bgColor=textLighter,
                highlight=highlightLight,
                highlightedText=text,
                text=text,
                borderColor=mid,
                bw=0,
            )
    # Add scrollbar
    SS += simpleScrollBarV(handle=mid, width=10)
    return strformat(SS)
def toolBarSS():
    return getStyleSheet('toolBarSS').format(border=midlighter,)
def verticalToolButtonSS():
    return getStyleSheet('verticalToolButtonSS').format(borderColor=mid,bgChecked=textLighter,bgHover=highlightLight,)
def getminorSS(name=''):
    global minor, minordict
    if minor:return minordict.get(name, minor)
    minor= getStyleSheet('minorSS').format(header=highlightLight, button=button, window=window, line=mid, highlight=highlight, bg=highlightLight,text=highlightedTextDark)
    minordict.clear()
    minordict.update(css_to_dict(minor))
    return minordict.get(name, minor)
def dockSS():
    return getminorSS('dockSS')     
def searchResultSS():
    return getminorSS('searchResultSS')
def lineEditSS():
    # return "border-radius: 6px;"
    return getminorSS('lineEditSS')
def transparentSS():
    return getminorSS('transparentSS')
def simpleScrollBarV(handle:str|None=None, width=8):
    # system default is (i think): mid background, dark handle
    default = midlighter
    handle = handle or midlighter
    return getStyleSheet('simpleScrollBarV').format(background="transparent",handle=handle,width=width)
def toolBoxSS():
    return getStyleSheet('toolBoxSS').format(background=highlightLight, backgroundHover=highlight, colorHover=highlightedText)
def titleLabelSS():
    return getminorSS('titleLabelSS')
