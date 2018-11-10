#!/usr/bin/env python
# --!-- coding: utf8 --!--

# Lots of stuff from here comes from the excellent focuswriter.
import os
import re

from PyQt5.QtCore import QSettings, QRect, QSize, Qt, QPoint, QFile, QIODevice, QTextStream
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QImage, QTextBlockFormat, QTextCharFormat, QFont, qGray
from PyQt5.QtWidgets import qApp, QFrame

from manuskript.functions import allPaths, appPath, findBackground, findFirstFile
from manuskript.ui.views.MDEditView import MDEditView

_thumbCache = {}

def loadThemeDatas(themeFile):
    settings = QSettings(themeFile, QSettings.IniFormat)
    _themeData = {}

    # Theme name
    _themeData["Name"] = getThemeName(themeFile)

    # Window Background
    loadThemeSetting(_themeData, settings, "Background/Color", "#000000")
    loadThemeSetting(_themeData, settings, "Background/ImageFile", "")
    loadThemeSetting(_themeData, settings, "Background/Type", 0)

    # Text Background
    loadThemeSetting(_themeData, settings, "Foreground/Color", "#ffffff")
    loadThemeSetting(_themeData, settings, "Foreground/Opacity", 50)
    loadThemeSetting(_themeData, settings, "Foreground/Margin", 40)
    loadThemeSetting(_themeData, settings, "Foreground/Padding", 10)
    loadThemeSetting(_themeData, settings, "Foreground/Position", 1)
    loadThemeSetting(_themeData, settings, "Foreground/Rounding", 5)
    loadThemeSetting(_themeData, settings, "Foreground/Width", 700)

    # Text Options
    loadThemeSetting(_themeData, settings, "Text/Color", "#ffffff")
    loadThemeSetting(_themeData, settings, "Text/Font", qApp.font().toString())
    loadThemeSetting(_themeData, settings, "Text/Misspelled", "#ff0000")

    # Paragraph Options
    loadThemeSetting(_themeData, settings, "Spacings/Alignment", 0)
    loadThemeSetting(_themeData, settings, "Spacings/IndentFirstLine", False)
    loadThemeSetting(_themeData, settings, "Spacings/LineSpacing", 100)
    loadThemeSetting(_themeData, settings, "Spacings/ParagraphAbove", 0)
    loadThemeSetting(_themeData, settings, "Spacings/ParagraphBelow", 0)
    loadThemeSetting(_themeData, settings, "Spacings/TabWidth", 48)

    return _themeData


def loadThemeSetting(datas, settings, key, default):
    """
    Loads data from ini file, using default value if the key is absent,
    and casting to the proper type based on default.
    """
    datas[key] = settings.value(key, default, type(default))

def getThemeName(theme):
    settings = QSettings(theme, QSettings.IniFormat)

    if settings.contains("Name"):
        return settings.value("Name")
    else:
        return os.path.splitext(os.path.split(theme)[1])[0]


def themeTextRect(themeDatas, screenRect):
    margin = themeDatas["Foreground/Margin"]
    x = 0
    y = margin
    width = min(themeDatas["Foreground/Width"], screenRect.width() - 2 * margin)
    height = screenRect.height() - 2 * margin

    if themeDatas["Foreground/Position"] == 0:  # Left
        x = margin
    elif themeDatas["Foreground/Position"] == 1:  # Center
        x = (screenRect.width() - width) / 2
    elif themeDatas["Foreground/Position"] == 2:  # Right
        x = screenRect.width() - margin - width
    elif themeDatas["Foreground/Position"] == 3:  # Stretched
        x = margin
        width = screenRect.width() - 2 * margin
    return QRect(x, y, width, height)


def createThemePreview(theme, screenRect, size=QSize(200, 120)):
    """
    Generates a QPixmap preview for given theme.

    Theme can be either a string containing the filename of the ini
    file with the theme settings, or it can be a dict with the settings.

    If theme is a filename, the result is cached.
    """

    # Checking whether theme is a string or dict
    if type(theme) == str and os.path.exists(theme):
        # Theme is the path to an ini file
        themeDatas = loadThemeDatas(theme)
        fromFile = True
    else:
        themeDatas = theme
        fromFile = False

    # Check if item is in cache
    if fromFile and theme in _thumbCache:
        if _thumbCache[theme][0] == themeDatas:
            return _thumbCache[theme][1]

    pixmap = generateTheme(themeDatas, screenRect)

    addThemePreviewText(pixmap, themeDatas, screenRect)

    px = QPixmap(pixmap).scaled(size, Qt.KeepAspectRatio)

    w = px.width() / 10
    h = px.height() / 10
    r = themeTextRect(themeDatas, screenRect)

    painter = QPainter(px)
    painter.drawPixmap(QRect(w, h, w * 4, h * 5), pixmap,
                       QRect(r.topLeft() - QPoint(w / 3, h / 3), QSize(w * 4, h * 5)))
    painter.setPen(Qt.white)
    painter.drawRect(QRect(w, h, w * 4, h * 5))
    painter.end()

    # If theme is a themefile, we keep it in cache
    if fromFile:
        _thumbCache[theme] = [themeDatas, px]

    return px


def findThemePath(themeName):
    p = findFirstFile(re.escape("{}.theme".format(themeName)), "resources/themes")
    if not p:
        return findFirstFile(r".*\.theme", "resources/themes")
    else:
        return p


def generateTheme(themeDatas, screenRect):
    # Window Background
    px = QPixmap(screenRect.size())
    px.fill(QColor(themeDatas["Background/Color"]))

    painter = QPainter(px)
    if themeDatas["Background/ImageFile"]:
        path = findBackground(themeDatas["Background/ImageFile"])
        _type = themeDatas["Background/Type"]
        if path and _type > 0:
            if _type == 1:  # Tiled
                painter.fillRect(screenRect, QBrush(QImage(path)))
            else:
                img = QImage(path)
                scaled = img.size()
                if _type == 3:  # Stretched
                    scaled.scale(screenRect.size(), Qt.IgnoreAspectRatio)
                elif _type == 4:  # Scaled
                    scaled.scale(screenRect.size(), Qt.KeepAspectRatio)
                elif _type == 5:  # Zoomed
                    scaled.scale(screenRect.size(), Qt.KeepAspectRatioByExpanding)

                painter.drawImage((screenRect.width() - scaled.width()) / 2,
                                  (screenRect.height() - scaled.height()) / 2, img.scaled(scaled))

    # Text Background
    textRect = themeTextRect(themeDatas, screenRect)

    painter.save()
    color = QColor(themeDatas["Foreground/Color"])
    color.setAlpha(themeDatas["Foreground/Opacity"] * 255 / 100)
    painter.setBrush(color)
    painter.setPen(Qt.NoPen)
    r = themeDatas["Foreground/Rounding"]
    painter.drawRoundedRect(textRect, r, r)
    painter.restore()

    painter.end()
    return px


def themeEditorGeometry(themeDatas, textRect):
    padding = themeDatas["Foreground/Padding"]
    x = textRect.x() + padding
    y = textRect.y() + padding + themeDatas["Spacings/ParagraphAbove"]
    width = textRect.width() - 2 * padding
    height = textRect.height() - 2 * padding - themeDatas["Spacings/ParagraphAbove"]
    return x, y, width, height


def getThemeBlockFormat(themeDatas):
    bf = QTextBlockFormat()
    bf.setAlignment(Qt.AlignLeft if themeDatas["Spacings/Alignment"] == 0 else
                    Qt.AlignCenter if themeDatas["Spacings/Alignment"] == 1 else
                    Qt.AlignRight if themeDatas["Spacings/Alignment"] == 2 else
                    Qt.AlignJustify)
    bf.setLineHeight(themeDatas["Spacings/LineSpacing"], QTextBlockFormat.ProportionalHeight)
    bf.setTextIndent(themeDatas["Spacings/TabWidth"] * 1 if themeDatas["Spacings/IndentFirstLine"] else 0)
    bf.setTopMargin(themeDatas["Spacings/ParagraphAbove"])
    bf.setBottomMargin(themeDatas["Spacings/ParagraphBelow"])
    return bf


def setThemeEditorDatas(editor, themeDatas, pixmap, screenRect):
    textRect = themeTextRect(themeDatas, screenRect)
    x, y, width, height = themeEditorGeometry(themeDatas, textRect)
    editor.setGeometry(x, y, width, height)

    # p = editor.palette()
    ##p.setBrush(QPalette.Base, QBrush(pixmap.copy(x, y, width, height)))
    # p.setBrush(QPalette.Base, QColor(Qt.transparent))
    # p.setColor(QPalette.Text, QColor(themeDatas["Text/Color"]))
    # p.setColor(QPalette.Highlight, QColor(themeDatas["Text/Color"]))
    # p.setColor(QPalette.HighlightedText, Qt.black if qGray(QColor(themeDatas["Text/Color"]).rgb()) > 127 else Qt.white)
    # editor.setPalette(p)

    editor.setAttribute(Qt.WA_NoSystemBackground, True)

    bf = getThemeBlockFormat(themeDatas)
    editor.setDefaultBlockFormat(bf)

    # b = editor.document().firstBlock()
    # cursor = editor.textCursor()
    # cursor.setBlockFormat(bf)
    # while b.isValid():
    # bf2 = b.blockFormat()
    # bf2.merge(bf)
    # cursor.setPosition(b.position())
    ##cursor.setPosition(b.position(), QTextCursor.KeepAnchor)
    # cursor.setBlockFormat(bf2)
    # b = b.next()

    editor.setTabStopWidth(themeDatas["Spacings/TabWidth"])
    editor.document().setIndentWidth(themeDatas["Spacings/TabWidth"])

    editor.highlighter.setMisspelledColor(QColor(themeDatas["Text/Misspelled"]))

    cf = QTextCharFormat()
    # f = QFont()
    # f.fromString(themeDatas["Text/Font"])
    # cf.setFont(f)
    editor.highlighter.setDefaultCharFormat(cf)
    f = QFont()
    f.fromString(themeDatas["Text/Font"])
    # editor.setFont(f)

    editor.setStyleSheet("""
        background: transparent;
        color: {foreground};
        font-family: {ff};
        font-size: {fs};
        selection-color: {sc};
        selection-background-color: {sbc};
        """.format(
            foreground=themeDatas["Text/Color"],
            ff=f.family(),
            fs="{}pt".format(str(f.pointSize())),
            sc="black" if qGray(QColor(themeDatas["Text/Color"]).rgb()) > 127 else "white",
            sbc=themeDatas["Text/Color"],
    )
    )

    editor._fromTheme = True
    editor._themeData = themeDatas
    editor.highlighter.updateColorScheme()

def addThemePreviewText(pixmap, themeDatas, screenRect):
    # Text
    previewText = MDEditView(highlighting=True)
    previewText.setFrameStyle(QFrame.NoFrame)
    previewText.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    previewText.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    f = QFile(appPath("resources/themes/preview.txt"))
    f.open(QIODevice.ReadOnly)
    previewText.setPlainText(QTextStream(f).readAll())

    setThemeEditorDatas(previewText, themeDatas, pixmap, screenRect)

    previewText.render(pixmap, previewText.pos())

    ## Text Background
    ##themeDatas["Foreground/Color"]
    ##themeDatas["Foreground/Opacity"]
    ##themeDatas["Foreground/Margin"]
    ##themeDatas["Foreground/Padding"]
    ##themeDatas["Foreground/Position"]
    ##themeDatas["Foreground/Rounding"]
    ##themeDatas["Foreground/Width"]

    ## Text Options
    ##themeDatas["Text/Color"]
    ##themeDatas["Text/Font"]
    # themeDatas["Text/Misspelled"]

    ## Paragraph Options
    ##themeDatas["Spacings/IndentFirstLine"]
    ##themeDatas["Spacings/LineSpacing"]
    ##themeDatas["Spacings/ParagraphAbove"]
    ##themeDatas["Spacings/ParagraphBelow"]
    ##themeDatas["Spacings/TabWidth"]
