#!/usr/bin/env python
#--!-- coding: utf8 --!--

import os
import re
import sys
import pathlib
from random import *

from PyQt5.QtCore import Qt, QRect, QStandardPaths, QObject, QProcess, QRegExp
from PyQt5.QtCore import QDir, QUrl, QTimer
from PyQt5.QtGui import QBrush, QIcon, QPainter, QColor, QImage, QPixmap
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import qApp, QFileDialog

from manuskript.enums import Outline

import logging
LOGGER = logging.getLogger(__name__)

# Used to detect multiple connections
AUC = Qt.AutoConnection | Qt.UniqueConnection
MW = None


def wordCount(text):
    return len(re.findall(r"\S+", text))


def charCount(text, use_spaces = True):
    if use_spaces:
        return len(re.findall(r"[\S ]", text))
    else:
        return len(re.findall(r"\S", text))

validate_ok = lambda *args, **kwargs: True
def uiParse(input, default, converter, validator=validate_ok):
    """
    uiParse is a utility function that intends to make it easy to convert
    user input to data that falls in the range of expected values the
    program is expecting to handle.

    It swallows all exceptions that happen during conversion.
    The validator should return True to permit the converted value.
    """
    result = default
    try:
        result = converter(input)
    except:
        pass  # failed to convert

    # Whitelist default value in case default type differs from converter output.
    if (result != default) and not validator(result):
        result = default
    return result


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
    progress = toFloat(progress)  # handle invalid input (issue #561)
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
    POV = item.data(Outline.POV)
    if POV == "":
        col = QColor(Qt.transparent)
    else:
        for i in range(mw.mdlCharacter.rowCount()):
            if mw.mdlCharacter.ID(i) == POV:
                colors["POV"] = iconColor(mw.mdlCharacter.icon(i))

    # Label
    lbl = item.data(Outline.label)
    if lbl == "":
        col = QColor(Qt.transparent)
    else:
        col = iconColor(mw.mdlLabels.item(toInt(lbl)).icon())
    # if col == Qt.black:
    #     # Don't know why, but transparent is rendered as black
    #     col = QColor(Qt.transparent)
    colors["Label"] = col

    # Progress
    pg = item.data(Outline.goalPercentage)
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
    p = os.path.realpath(os.path.join(os.path.split(__file__)[0], "../.."))
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

def statusMessage(message, duration=5000, importance=1):
    """
    Shows a message in MainWindow's status bar.
    Importance: 0 = low, 1 = normal, 2 = important, 3 = critical.
    """
    from manuskript.ui import style as S
    MW.statusBar().hide()
    MW.statusLabel.setText(message)
    if importance == 0:
        MW.statusLabel.setStyleSheet("color:{};".format(S.textLighter))
    elif importance == 1:
        MW.statusLabel.setStyleSheet("color:{};".format(S.textLight))
    elif importance == 2:
        MW.statusLabel.setStyleSheet("color:{}; font-weight: bold;".format(S.text))
    elif importance == 3:
        MW.statusLabel.setStyleSheet("color:red; font-weight: bold;")
    MW.statusLabel.adjustSize()
    g = MW.statusLabel.geometry()
    # g.moveCenter(MW.mapFromGlobal(MW.geometry().center()))
    s = MW.layout().spacing() / 2
    g.setLeft(s)
    g.moveBottom(MW.mapFromGlobal(MW.geometry().bottomLeft()).y() - s)
    MW.statusLabel.setGeometry(g)
    MW.statusLabel.show()
    QTimer.singleShot(duration, MW.statusLabel.hide)

def openURL(url):
    """
    Opens url (string) in browser using desktop default application.
    """
    QDesktopServices.openUrl(QUrl(url))

def getSaveFileNameWithSuffix(parent, caption, directory, filter, options=None, selectedFilter=None, defaultSuffix=None):
    """
    A reimplemented version of QFileDialog.getSaveFileName() because we would like to make use
    of the QFileDialog.defaultSuffix property that getSaveFileName() does not let us adjust.

    Note: knowing the selected filter is not an invitation to change the chosen filename later.
    """
    dialog = QFileDialog(parent=parent, caption=caption, directory=directory, filter=filter)
    if options:
        dialog.setOptions(options)
    if defaultSuffix:
        dialog.setDefaultSuffix(defaultSuffix)
    dialog.setFileMode(QFileDialog.AnyFile)
    if hasattr(dialog, 'setSupportedSchemes'): # Pre-Qt5.6 lacks this.
        dialog.setSupportedSchemes(("file",))
    dialog.setAcceptMode(QFileDialog.AcceptSave)
    if selectedFilter:
        dialog.selectNameFilter(selectedFilter)
    if (dialog.exec() == QFileDialog.Accepted):
        return dialog.selectedFiles()[0], dialog.selectedNameFilter()
    return None, None

def inspect():
    """
    Debugging tool. Call it to see a stack of calls up to that point.
    """
    import inspect, os
    print("-----------------------")
    for s in inspect.stack()[1:]:
        print(" * {}:{} // {}".format(
            os.path.basename(s.filename),
            s.lineno,
            s.function))
        print("   " + "".join(s.code_context))


def search(searchRegex, text):
    """
    Search all occurrences of a regex in a text.

    :param searchRegex:    a regex object with the search to perform
    :param text:            text to search on
    :return:                list of tuples (startPos, endPos)
    """
    if text is not None:
        return [(m.start(), m.end(), getSearchResultContext(text, m.start(), m.end())) for m in searchRegex.finditer(text)]
    else:
        return []

def getSearchResultContext(text, startPos, endPos):
    matchSize = endPos - startPos
    maxContextSize = max(matchSize, 600)
    extraContextSize = int((maxContextSize - matchSize) / 2)
    separator = "[...]"

    context = ""

    i = startPos - 1
    while i > 0 and (startPos - i) < extraContextSize and text[i] != '\n':
        i -= 1
    contextStartPos = i
    if i > 0:
        context += separator + " "
    context += text[contextStartPos:startPos].replace('\n', '')

    context += '<b>' + text[startPos:endPos].replace('\n', '') + '</b>'

    i = endPos
    while i < len(text) and (i - endPos) < extraContextSize and text[i] != '\n':
        i += 1
    contextEndPos = i

    context += text[endPos:contextEndPos].replace('\n', '')
    if i < len(text):
        context += " " + separator

    return context


# Based on answer by jfs at:
#  https://stackoverflow.com/questions/3718657/how-to-properly-determine-current-script-directory
def getManuskriptPath(follow_symlinks=True):
    """Used to obtain the path Manuskript is located at."""
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        import inspect
        path = inspect.getabsfile(getManuskriptPath) + "/../.."
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

# Based on answer by kagronik at:
#   https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script
def getGitRevision(base_path):
    """Get git revision without relying on external processes or libraries."""
    git_dir = pathlib.Path(base_path) / '.git'
    if not git_dir.exists():
        return None

    with (git_dir / 'HEAD').open('r') as head:
        ref = head.readline().split(' ')[-1].strip()

    with (git_dir / ref).open('r') as git_hash:
        return git_hash.readline().strip()

def getGitRevisionAsString(base_path, short=False):
    """Catches errors and presents a nice string."""
    try:
        rev = getGitRevision(base_path)
        if rev is not None:
            if short:
                rev = rev[:7]
            return "#" + rev
        else:
            return ""  # not a git repository
    except Exception as e:
        LOGGER.warning("Failed to obtain Git revision: %s", e)
        return "#ERROR"

def showInFolder(path, open_file_as_fallback=False):
    '''
    Show a file or folder in explorer/finder, highlighting it where possible.
    Source: https://stackoverflow.com/a/46019091/3388962
    '''
    path = os.path.abspath(path)
    dirPath = path if os.path.isdir(path) else os.path.dirname(path)
    if sys.platform == 'win32':
        args = []
        args.append('/select,')
        args.append(QDir.toNativeSeparators(path))
        if QProcess.startDetached('explorer', args):
            return True
    elif sys.platform == 'darwin':
        args = []
        args.append('-e')
        args.append('tell application "Finder"')
        args.append('-e')
        args.append('activate')
        args.append('-e')
        args.append('select POSIX file "%s"' % path)
        args.append('-e')
        args.append('end tell')
        args.append('-e')
        args.append('return')
        if not QProcess.execute('/usr/bin/osascript', args):
            return True
        #if not QtCore.QProcess.execute('/usr/bin/open', [dirPath]):
        #    return
    # TODO: Linux is not implemented. It has many file managers (nautilus, xdg-open, etc.)
    # each of which needs special ways to highlight a file in a file manager window.

    # Fallback.
    return QDesktopServices.openUrl(QUrl(path if open_file_as_fallback else dirPath))


# Spellchecker loads writablePath from this file, so we need to load it after they get defined
from manuskript.functions.spellchecker import Spellchecker
