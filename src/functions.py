#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *

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
    
def drawProgress(painter, rect, progress, radius=0):
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#dddddd"))
    painter.drawRoundedRect(rect, radius, radius)
    
    c1 = QColor(Qt.red)
    c2 = QColor(Qt.blue)
    c3 = QColor(Qt.darkGreen)
    c4 = QColor("#FFA500")
    
    if progress < 0.3:
        painter.setBrush(QBrush(c1))
    elif progress < 0.8:
        painter.setBrush(QBrush(c2))
    elif progress > 1.2:
        painter.setBrush(QBrush(c4))
    else:
        painter.setBrush(QBrush(c3))
        
    r2 = QRect(rect)
    r2.setWidth(r2.width() * min(progress, 1))
    painter.drawRoundedRect(r2, radius, radius)
    
def mainWindow():
    for i in qApp.topLevelWidgets():
        if i.objectName() == "MainWindow":
            return i
    return None

def iconColor(icon):
    "Returns a QRgb from a QIcon, assuming its all the same color"
    return QColor(QImage(icon.pixmap(5, 5)).pixel(2, 2))