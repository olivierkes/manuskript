#!/usr/bin/env python
#--!-- coding: utf8 --!--

import os
import re
from random import *

from PyQt5.QtCore import Qt, QRect, QStandardPaths, QObject, QRegExp, QDir
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QBrush, QIcon, QPainter, QColor, QImage, QPixmap
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import qApp, QTextEdit

from manuskript.enums import Outline

# Used to detect multiple connections
AUC = Qt.AutoConnection | Qt.UniqueConnection
MW = None


def wordCount(text):
    t = text.strip().replace(" ", "\n").split("\n")
    t = [l for l in t if l]
    return len(t)


def toInt(text):
    if text:
        try:
            return int(text)
        except ValueError:
            pass

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
    from manuskript.ui import style as S
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(S.base)) # "#dddddd"
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
    global MW
    if not MW:
        for i in qApp.topLevelWidgets():
            if i.objectName() == "MainWindow":
                MW = i
                return MW
        return None
    else:
        return MW


def iconColor(icon):
    """Returns a QRgb from a QIcon, assuming its all the same color"""
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


def themeIcon(name):
    "Returns an icon for the given name."

    db = {
        "character":    "stock_people",
        "characters":   "stock_people",
        "plot":         "stock_shuffle",
        "plots":        "stock_shuffle",
        "world":        "emblem-web", #stock_timezone applications-internet
        "outline":      "gtk-index", #applications-versioncontrol
        "label":        "folder_color_picker",
        "status":       "applications-development",
        "text":         "view-text",
        "card":         "view-card",
        "outline":      "view-outline",
        "tree":         "view-list-tree",
        "spelling":     "tools-check-spelling"
    }

    if name in db:
        return QIcon.fromTheme(db[name])
    else:
        return QIcon()

def randomColor(mix=None):
    """Generates a random color. If mix (QColor) is given, mixes the random color and mix."""
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)

    if mix:
        r = (r + mix.red()) / 2
        g = (g + mix.green()) / 2
        b = (b + mix.blue()) / 2

    return QColor(r, g, b)


def mixColors(col1, col2, f=.5):
    fromString = False
    if type(col1) == str:
        fromString = True
        col1 = QColor(col1)
    if type(col2) == str:
        col2 = QColor(col2)
    f2 = 1-f
    r = col1.red() * f + col2.red() * f2
    g = col1.green() * f + col2.green() * f2
    b = col1.blue() * f + col2.blue() * f2

    return QColor(r, g, b) if not fromString else QColor(r, g, b).name()


def outlineItemColors(item):

    from manuskript.ui import style as S

    """Takes an OutlineItem and returns a dict of colors."""
    colors = {}
    mw = mainWindow()

    # POV
    colors["POV"] = QColor(Qt.transparent)
    POV = item.data(Outline.POV.value)
    if POV == "":
        col = QColor(Qt.transparent)
    else:
        for i in range(mw.mdlCharacter.rowCount()):
            if mw.mdlCharacter.ID(i) == POV:
                colors["POV"] = iconColor(mw.mdlCharacter.icon(i))

    # Label
    lbl = item.data(Outline.label.value)
    if lbl == "":
        col = QColor(Qt.transparent)
    else:
        col = iconColor(mw.mdlLabels.item(toInt(lbl)).icon())
    # if col == Qt.black:
    #     # Don't know why, but transparent is rendered as black
    #     col = QColor(Qt.transparent)
    colors["Label"] = col

    # Progress
    pg = item.data(Outline.goalPercentage.value)
    colors["Progress"] = colorFromProgress(pg)

    # Compile
    if item.compile() in [0, "0"]:
        colors["Compile"] = mixColors(QColor(S.text), QColor(S.window))
    else:
        colors["Compile"] = QColor(Qt.transparent) # will use default

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

def tempFile(name):
    "Returns a temp file."
    return os.path.join(QDir.tempPath(), name)


def totalObjects():
    return len(mainWindow().findChildren(QObject))


def printObjects():
    print("Objects:", str(totalObjects()))


def findWidgetsOfClass(cls):
    """
    Returns all widgets, children of MainWindow, whose class is cls.
    @param cls: a class
    @return: list of QWidgets
    """
    return mainWindow().findChildren(cls, QRegExp())


def findBackground(filename):
    """
    Returns the full path to a background file of name filename within resources folders.
    """
    return findFirstFile(re.escape(filename), "resources/backgrounds")


def findFirstFile(regex, path="resources"):
    """
    Returns full path of first file matching regular expression regex within folder path,
    otherwise returns full path of last file in folder path.
    """
    paths = allPaths(path)
    for p in paths:
        lst = os.listdir(p)
        for l in lst:
            if re.match(regex, l):
                return os.path.join(p, l)

def customIcons():
    """
    Returns a list of possible customIcons. String from theme.
    """

    r = [
        "text-plain",
        "gnome-settings",
        "applications-internet",
        "applications-debugging",
        "applications-development",
        "system-help",
        "info",
        "dialog-question",
        "dialog-warning",
        "stock_timezone",
        "stock_people",
        "stock_shuffle",
        "gtk-index",
        "folder_color_picker",
        "applications-versioncontrol",

        "stock_home",
        "stock_trash_empty",
        "stock_trash_full",
        "stock_yes",
        "stock_no",
        "stock_notes",
        "stock_calendar",
        "stock_mic",
        'stock_score-lowest', 'stock_score-lower', 'stock_score-low', 'stock_score-normal', 'stock_score-high', 'stock_score-higher', 'stock_score-highest',
        "stock_task",
        "stock_refresh",
        "application-community",
        "applications-chat",
        "application-menu",
        "applications-education",
        "applications-science",
        "applications-puzzles",
        "applications-roleplaying",
        "applications-sports",
        "applications-libraries",
        "applications-publishing",
        "applications-development",
        "applications-games",
        "applications-boardgames",
        "applications-geography",
        "applications-physics",
        "package_multimedia",
        "media-flash",
        "media-optical",
        "media-floppy",
        "media-playback-start",
        "media-playback-pause",
        "media-playback-stop",
        "media-playback-record",
        "media-playback-start-rtl",
        "media-eject",
        "document-save",
        "gohome",
        'purple-folder', 'yellow-folder', 'red-folder', 'custom-folder', 'grey-folder', 'blue-folder', 'default-folder', 'pink-folder', 'orange-folder', 'green-folder', 'brown-folder',
        'folder-home', 'folder-remote', 'folder-music', 'folder-saved-search', 'folder-projects', 'folder-sound', 'folder-publicshare', 'folder-pictures', 'folder-saved-search-alt', 'folder-tag',
        'calendar-01', 'calendar-02', 'calendar-03', 'calendar-04', 'calendar-05', 'calendar-06', 'calendar-07', 'calendar-08', 'calendar-09', 'calendar-10',
        'arrow-down', 'arrow-left', 'arrow-right', 'arrow-up', 'arrow-down-double', 'arrow-left-double', 'arrow-right-double', 'arrow-up-double',
        'emblem-added', 'emblem-checked', 'emblem-downloads', 'emblem-dropbox-syncing', 'emblem-danger', 'emblem-development', 'emblem-dropbox-app', 'emblem-art', 'emblem-camera', 'emblem-dropbox-selsync', 'emblem-insync-des-error', 'emblem-insync-error', 'emblem-generic', 'emblem-favorites', 'emblem-error', 'emblem-dropbox-uptodate', 'emblem-marketing', 'emblem-money', 'emblem-music', 'emblem-noread', 'emblem-people', 'emblem-personal', 'emblem-sound', 'emblem-shared', 'emblem-sales', 'emblem-presentation', 'emblem-plan', 'emblem-system', 'emblem-urgent', 'emblem-videos', 'emblem-web',
        'face-angel', 'face-clown', 'face-angry', 'face-cool', 'face-devilish', 'face-sick', 'face-sleeping', 'face-uncertain', 'face-monkey', 'face-ninja', 'face-pirate', 'face-glasses', 'face-in-love', 'face-confused',
        'feed-marked-symbolic', 'feed-non-starred', 'feed-starred', 'feed-unmarked-symbolic',
        'notification-new-symbolic',
        ]

    return sorted(r)


def statusMessage(message, duration=5000):
    mainWindow().statusBar().showMessage(message, duration)


def openURL(url):
    QDesktopServices.openUrl(QUrl(url))
