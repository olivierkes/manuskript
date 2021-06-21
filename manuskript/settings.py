# -*- coding: utf-8 -*-

import collections
import json

from PyQt5.QtWidgets import qApp

from manuskript.enums import Outline

import logging
LOGGER = logging.getLogger(__name__)

# TODO: move some/all of those settings to application settings and not project settings
#       in order to allow a shared project between several writers

viewSettings = {
    "Tree": {
        "Icon": "Nothing",
        "Text": "Compile",
        "Background": "Nothing",
        "InfoFolder": "Nothing",
        "InfoText": "Nothing",
        "iconSize": 24,
        },
    "Cork": {
        "Icon": "Nothing",
        "Text": "Nothing",
        "Background": "Nothing",
        "Corner": "Label",
        "Border": "Nothing",
        },
    "Outline": {
        "Icon": "Nothing",
        "Text": "Compile",
        "Background": "Nothing",
        },
    }

fullscreenSettings = {
    "autohide-top": True,
    "autohide-bottom": True,
    "autohide-left": True,
    }

# Application
spellcheck = False
dict = None
corkSizeFactor = 100
folderView = "cork"
lastTab = 0
openIndexes = [""]
progressChars = False
countSpaces = True
autoSave = False
autoSaveDelay = 5
autoSaveNoChanges = True
autoSaveNoChangesDelay = 5
saveOnQuit = True
outlineViewColumns = [Outline.title, Outline.POV, Outline.status,
                      Outline.compile, Outline.wordCount, Outline.goal,
                      Outline.goalPercentage, Outline.label]
corkBackground = {
    "color": "#926239",
    "image": "writingdesk"
        }
corkStyle = "new"
defaultTextType = "md"
fullScreenTheme = "spacedreams"

textEditor = {
    "background": "",
    "fontColor": "",
    "font": qApp.font().toString(),
    "misspelled": "#F00",
    "lineSpacing": 100,
    "tabWidth": 20,
    "indent": False,
    "spacingAbove": 5,
    "spacingBelow": 5,
    "textAlignment": 0, # 0: left, 1: center, 2: right, 3: justify
    "cursorWidth": 1,
    "cursorNotBlinking": False,
    "maxWidth": 600,
    "marginsLR": 0,
    "marginsTB": 20,
    "backgroundTransparent": False,
    "alwaysCenter": False,
    "focusMode": False  # "line", "paragraph", "sentence"
    }

revisions = {
    "keep": False,
    "smartremove": True,
    "rules": collections.OrderedDict({
        10 * 60:            60,                     # One per minute for the last 10mn
        60 * 60:            60 * 10,                # One per 10mn for the last hour
        60 * 60 * 24:       60 * 60,                # One per hour for the last day
        60 * 60 * 24 * 30:  60 * 60 * 24,           # One per day for the last month
        None:               60 * 60 * 24 * 7,       # One per week for eternity
        })
    }

frequencyAnalyzer = {
    "wordMin": 1,
    "wordExclude": "a, and, or",
    "phraseMin": 2,
    "phraseMax": 5
}

viewMode = "fiction"  # simple, fiction
saveToZip = True
dontShowDeleteWarning = False

def initDefaultValues():
    """
    Load some default values based on system's settings.
    Is called anytime we open/create a project.
    """
    global textEditor
    if not textEditor["background"]:
        from manuskript.ui import style as S
        textEditor["background"] = S.base
    if not textEditor["fontColor"]:
        from manuskript.ui import style as S
        textEditor["fontColor"] = S.text

def save(filename=None, protocol=None):

    global spellcheck, dict, corkSliderFactor, viewSettings, corkSizeFactor, folderView, lastTab, openIndexes, \
           progressChars, autoSave, autoSaveDelay, saveOnQuit, autoSaveNoChanges, autoSaveNoChangesDelay, outlineViewColumns, \
           corkBackground, corkStyle, fullScreenTheme, defaultTextType, textEditor, revisions, frequencyAnalyzer, viewMode, \
           saveToZip, dontShowDeleteWarning, fullscreenSettings

    allSettings = {
        "viewSettings": viewSettings,
        "fullscreenSettings": fullscreenSettings,
        "dict": dict,
        "spellcheck": spellcheck,
        "corkSizeFactor": corkSizeFactor,
        "folderView": folderView,
        "lastTab": lastTab,
        "openIndexes": openIndexes,
        "progressChars": progressChars,
        "countSpaces": countSpaces,
        "autoSave":autoSave,
        "autoSaveDelay":autoSaveDelay,
        # TODO: Settings Cleanup Task -- Rename saveOnQuit to saveOnProjectClose -- see PR #615
        "saveOnQuit":saveOnQuit,
        "autoSaveNoChanges":autoSaveNoChanges,
        "autoSaveNoChangesDelay":autoSaveNoChangesDelay,
        "outlineViewColumns":outlineViewColumns,
        "corkBackground":corkBackground,
        "corkStyle": corkStyle,
        "fullScreenTheme":fullScreenTheme,
        "defaultTextType":defaultTextType,
        "textEditor":textEditor,
        "revisions":revisions,
        "frequencyAnalyzer": frequencyAnalyzer,
        "viewMode": viewMode,
        "saveToZip": saveToZip,
        "dontShowDeleteWarning": dontShowDeleteWarning,
    }

    #pp=pprint.PrettyPrinter(indent=4, compact=False)
    #print("Saving:")
    #pp.pprint(allSettings)

    # This looks stupid
    # But a simple json.dumps with sort_keys will throw a TypeError
    # because of unorderable types.
    return json.dumps(json.loads(json.dumps(allSettings)), indent=4, sort_keys=True)


def load(string, fromString=False, protocol=None):
    """fromString=True is deprecated, it shouldn't be used."""
    global allSettings

    if not string:
        LOGGER.error("Cannot load settings.")
        return

    allSettings = json.loads(string)

    #pp=pprint.PrettyPrinter(indent=4, compact=False)
    #print("Loading:")
    #pp.pprint(allSettings)

    # FIXME: use dict.update(dict) to update settings in newer versions.

    if "viewSettings" in allSettings:
        global viewSettings
        viewSettings = allSettings["viewSettings"]

        for cat, name, default in [
            ("Tree", "iconSize", 24),   # Added in 0.6.0
            ]:
            if not name in viewSettings[cat]:
                viewSettings[cat][name] = default

    if "fullscreenSettings" in allSettings:
        global fullscreenSettings
        fullscreenSettings = allSettings["fullscreenSettings"]

    if "dict" in allSettings:
        global dict
        dict = allSettings["dict"]

    if "spellcheck" in allSettings:
        global spellcheck
        spellcheck = allSettings["spellcheck"]

    if "corkSizeFactor" in allSettings:
        global corkSizeFactor
        corkSizeFactor = allSettings["corkSizeFactor"]

    if "folderView" in allSettings:
        global folderView
        folderView = allSettings["folderView"]

    if "lastTab" in allSettings:
        global lastTab
        lastTab = allSettings["lastTab"]

    if "openIndexes" in allSettings:
        global openIndexes
        openIndexes = allSettings["openIndexes"]

    if "progressChars" in allSettings:
        global progressChars
        progressChars = allSettings["progressChars"]

    if "countSpaces" in allSettings:
        global countSpaces
        countSpaces = allSettings["countSpaces"]

    if "autoSave" in allSettings:
        global autoSave
        autoSave = allSettings["autoSave"]

    if "autoSaveDelay" in allSettings:
        global autoSaveDelay
        autoSaveDelay = allSettings["autoSaveDelay"]

    if "saveOnQuit" in allSettings:
        global saveOnQuit
        saveOnQuit = allSettings["saveOnQuit"]

    if "autoSaveNoChanges" in allSettings:
        global autoSaveNoChanges
        autoSaveNoChanges = allSettings["autoSaveNoChanges"]

    if "autoSaveNoChangesDelay" in allSettings:
        global autoSaveNoChangesDelay
        autoSaveNoChangesDelay = allSettings["autoSaveNoChangesDelay"]

    if "outlineViewColumns" in allSettings:
        global outlineViewColumns
        outlineViewColumns = allSettings["outlineViewColumns"]

    if "corkBackground" in allSettings:
        global corkBackground
        corkBackground = allSettings["corkBackground"]

    if "corkStyle" in allSettings:
        global corkStyle
        corkStyle = allSettings["corkStyle"]

    if "fullScreenTheme" in allSettings:
        global fullScreenTheme
        fullScreenTheme = allSettings["fullScreenTheme"]

    if "defaultTextType" in allSettings:
        global defaultTextType
        defaultTextType = allSettings["defaultTextType"]

    if "textEditor" in allSettings:
        global textEditor
        textEditor = allSettings["textEditor"]

        added = {
            "textAlignment": 0,                 # Added in 0.5.0
            "cursorWidth": 1,
            "cursorNotBlinking": False,         # Added in 0.6.0
            "maxWidth": 600,
            "marginsLR": 0,
            "marginsTB": 20,
            "backgroundTransparent": False,      # Added in 0.6.0
            "alwaysCenter": False,               # Added in 0.7.0
            "focusMode": False,
            }

        for k in added:
            if not k in textEditor: textEditor[k] = added[k]

        if textEditor["cursorNotBlinking"]:
            qApp.setCursorFlashTime(0)
        else:
            from manuskript.functions import mainWindow
            qApp.setCursorFlashTime(mainWindow()._defaultCursorFlashTime)

    if "revisions" in allSettings:
        global revisions
        revisions = allSettings["revisions"]

        # With JSON we had to convert int keys to str, and None to "null", so we roll back.
        r = {}
        for i in revisions["rules"]:
            if i == "null":
                r[None] = revisions["rules"]["null"]

            elif i == None:
                r[None] = revisions["rules"][None]

            else:
                r[int(i)] = revisions["rules"][i]

        revisions["rules"] = r

    if "frequencyAnalyzer" in allSettings:
        global frequencyAnalyzer
        frequencyAnalyzer = allSettings["frequencyAnalyzer"]

    if "viewMode" in allSettings:
        global viewMode
        viewMode = allSettings["viewMode"]

    if "saveToZip" in allSettings:
        global saveToZip
        saveToZip = allSettings["saveToZip"]

    if "dontShowDeleteWarning" in allSettings:
        global dontShowDeleteWarning
        dontShowDeleteWarning = allSettings["dontShowDeleteWarning"]
