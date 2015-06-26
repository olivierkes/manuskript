#!/usr/bin/env python
#--!-- coding: utf8 --!--

from qt import *
from random import *
from enums import *
import os

# Used to detect multiple connections
AUC = Qt.AutoConnection | Qt.UniqueConnection

def wordCount(text):
    return len(text.strip().replace(" ", "\n").split("\n")) if text else 0

def toInt(text):
    if text:
        return int(text)
    else:
        return 0
    
def toFloat(text):
    if text:
        return float(text)
    else:
        return 0.
    
def toString(text):
    if text in [None, "None"]:
        return ""
    else:
        return str(text)
    
def drawProgress(painter, rect, progress, radius=0):
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#dddddd"))
    painter.drawRoundedRect(rect, radius, radius)
    
    painter.setBrush(QBrush(colorFromProgress(progress)))
        
    r2 = QRect(rect)
    r2.setWidth(r2.width() * min(progress, 1))
    painter.drawRoundedRect(r2, radius, radius)
    
def colorFromProgress(progress):
    progress = toFloat(progress)
    c1 = QColor(Qt.red)
    c2 = QColor(Qt.blue)
    c3 = QColor(Qt.darkGreen)
    c4 = QColor("#FFA500")
    
    if progress < 0.3:
        return c1
    elif progress < 0.8:
        return c2
    elif progress > 1.2:
        return c4
    else:
        return c3
    
def mainWindow():
    for i in qApp.topLevelWidgets():
        if i.objectName() == "MainWindow":
            return i
    return None

def iconColor(icon):
    "Returns a QRgb from a QIcon, assuming its all the same color"
    px = icon.pixmap(5, 5)
    if px.width() != 0:
        return QColor(QImage(px).pixel(2, 2))
    else:
        return QColor(Qt.transparent)

def iconFromColor(color):
    px = QPixmap(32, 32)
    px.fill(color)
    return QIcon(px)

def iconFromColorString(string):
    return iconFromColor(QColor(string))

def randomColor(mix=None):
    "Generates a random color. If mix (QColor) is given, mixes the random color and mix."
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    
    if mix:
        r = (r + mix.red()) / 2
        g = (g + mix.green()) / 2
        b = (b + mix.blue()) / 2
        
    return QColor(r, g, b)

def mixColors(col1, col2, f=.5):
    f2 = 1-f
    r = col1.red() * f + col2.red() * f2
    g = col1.green() * f + col2.green() * f2
    b = col1.blue() * f + col2.blue() * f2
    return QColor(r, g, b)

def outlineItemColors(item):
        "Takes an OutlineItem and returns a dict of colors."
        colors = {}
        mw = mainWindow()
        
        # POV
        colors["POV"] = QColor(Qt.transparent)
        POV = item.data(Outline.POV.value)
        for i in range(mw.mdlPersos.rowCount()):
            if mw.mdlPersos.item(i, Perso.ID.value).text() == POV:
                colors["POV"] = iconColor(mw.mdlPersos.item(i, 0).icon())
        
        # Label
        lbl = item.data(Outline.label.value)
        col = iconColor(mw.mdlLabels.item(toInt(lbl)).icon())
        if col == Qt.black:
            # Don't know why, but transparent is rendered as black
            col = QColor(Qt.transparent)
        colors["Label"] = col
        
        # Progress
        pg = item.data(Outline.goalPercentage.value)
        colors["Progress"] = colorFromProgress(pg)
        
        # Compile
        if item.compile() in [0, "0"]:
            colors["Compile"] = QColor(Qt.gray)
        else:
            colors["Compile"] = QColor(Qt.black)
            
        return colors
    
def colorifyPixmap(pixmap, color):
    # FIXME: ugly
    p = QPainter(pixmap)
    p.setCompositionMode(p.CompositionMode_Overlay)
    p.fillRect(pixmap.rect(), color)
    return pixmap

def appPath(suffix=None):
    p = os.path.realpath(os.path.join(os.path.split(__file__)[0], ".."))
    if suffix:
        p = os.path.join(p, suffix)
    return p

def writablePath(suffix=None):
    if hasattr(QStandardPaths, "AppLocalDataLocation"):
        p = QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
    else:
        # Qt < 5.4
        p = QStandardPaths.writableLocation(QStandardPaths.DataLocation)
    if suffix:
        p = os.path.join(p, suffix)
    if not os.path.exists(p):
        os.makedirs(p)
    return p

def allPaths(suffix=None):
    paths = []
    # src directory
    paths.append(appPath(suffix))
    # user writable directory
    paths.append(writablePath(suffix))
    return paths

def lightBlue():
    return QColor(Qt.blue).lighter(190)