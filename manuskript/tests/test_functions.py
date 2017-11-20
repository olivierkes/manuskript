#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for functions"""

from manuskript import functions as F

def test_wordCount():
    assert F.wordCount("In the beginning was the word.") == 6
    assert F.wordCount("") == 0

def test_convert():

    # toInt
    assert F.toInt("9") == 9
    assert F.toInt("a") == 0
    assert F.toInt("") == 0

    # toFloat
    assert F.toFloat("9.4") == 9.4
    assert F.toFloat("") == 0.

    # toString
    assert F.toString(None) == ""
    assert F.toString("None") == ""
    assert F.toString("Joy") == "Joy"

def test_several():

    from PyQt5.QtGui import QPainter, QPixmap, QIcon, QColor
    from PyQt5.QtCore import QRect

    # drawProgress
    px = QPixmap(10, 10)
    F.drawProgress(QPainter(px), QRect(0, 0, 100, 100), 0.5)

    # colorFromProgress
    a = F.colorFromProgress(0.1)
    b = F.colorFromProgress(0.5)
    c = F.colorFromProgress(1.0)
    d = F.colorFromProgress(1.5)
    assert a != b != c != d

    # iconColor & iconFromColor & iconFromColorString
    icon = F.iconFromColorString("#ff0000")
    assert F.iconColor(icon).name().lower() == "#ff0000"

    # themeIcon
    assert F.themeIcon("text") is not None
    assert F.themeIcon("nonexistingname") is not None

    # randomColor
    c1 = F.randomColor()
    c2 = F.randomColor(c1)
    assert c1.name() != c2.name()

    # mixColors
    c1 = QColor("#FFF")
    c2 = QColor("#000")
    assert F.mixColors(c1, c2).name() == "#7f7f7f"

    # colorifyPixmap
    assert F.colorifyPixmap(px, c1) != None

def test_outlineItemColors():

    from manuskript.models import outlineItem
    item = outlineItem(title="Test")

    r = F.outlineItemColors(item)
    for i in ["POV", "Label", "Progress", "Compile"]:
        assert i in r
    from PyQt5.QtGui import QColor
    assert r["Compile"].name(QColor.HexArgb) == "#00000000"

def test_paths():

    assert F.appPath() is not None
    assert F.writablePath is not None
    assert len(F.allPaths("suffix")) == 2
    assert F.tempFile("yop") is not None
    f = F.findBackground("spacedreams.jpg")
    assert "resources/backgrounds/spacedreams.jpg" in f
    assert len(F.customIcons()) > 1

def test_mainWindow():

    from PyQt5.QtWidgets import QWidget, QLCDNumber

    assert F.mainWindow() is not None
    assert F.MW is not None

    F.statusMessage("Test")
    F.printObjects()
    assert len(F.findWidgetsOfClass(QWidget)) > 0
    assert len(F.findWidgetsOfClass(QLCDNumber)) == 0
