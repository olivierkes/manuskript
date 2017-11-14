# -*- coding: utf-8 -*-

import collections
import json
import pickle

from PyQt5.QtWidgets import qApp

from manuskript.enums import Outline

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

# Application
spellcheck = False
dict = None
corkSizeFactor = 100
folderView = "cork"
lastTab = 0
openIndexes = [""]
autoSave = False
autoSaveDelay = 5
autoSaveNoChanges = True
autoSaveNoChangesDelay = 5
saveOnQuit = True
outlineViewColumns = [Outline.title.value, Outline.POV.value, Outline.status.value,
                      Outline.compile.value, Outline.wordCount.value, Outline.goal.value,
                      Outline.goalPercentage.value, Outline.label.value]
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
    "indent": True,
    "spacingAbove": 5,
    "spacingBelow": 5,
    "textAlignment": 0, # 0: left, 1: center, 2: right, 3: justify
    "cursorWidth": 1,
    "cursorNotBlinking": False,
    "maxWidth": 0,
    "marginsLR": 0,
    "marginsTB": 0,
    "backgroundTransparent": False,
    }

revisions = {
    "keep": True,
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
           autoSave, autoSaveDelay, saveOnQuit, autoSaveNoChanges, autoSaveNoChangesDelay, outlineViewColumns, \
           corkBackground, corkStyle, fullScreenTheme, defaultTextType, textEditor, revisions, frequencyAnalyzer, viewMode, \
           saveToZip, dontShowDeleteWarning

    allSettings = {
        "viewSettings": viewSettings,
        "dict": dict,
        "spellcheck": spellcheck,
        "corkSizeFactor": corkSizeFactor,
        "folderView": folderView,
        "lastTab": lastTab,
        "openIndexes": openIndexes,
        "autoSave":autoSave,
        "autoSaveDelay":autoSaveDelay,
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

    if filename:
        f = open(filename, "wb")
        pickle.dump(allSettings, f)
    else:
        if protocol == 0:
            # This looks stupid
            # But a simple json.dumps with sort_keys will throw a TypeError
            # because of unorderable types.
            return json.dumps(json.loads(json.dumps(allSettings)), indent=4, sort_keys=True)
        else:
           return pickle.dumps(allSettings)


def load(string, fromString=False, protocol=None):
    """Load settings from 'string'. 'string' is the filename of the pickle dump.
    If fromString=True, string is the data of the pickle dumps."""
    global allSettings

    if not fromString:
        try:
            f = open(string, "rb")
            allSettings = pickle.load(f)

        except:
            print("{} doesn't exist, cannot load settings.".format(string))
            return
    else:
        if protocol == 0:
            allSettings = json.loads(string)
        else:
            allSettings = pickle.loads(string)

    #pp=pprint.PrettyPrinter(indent=4, compact=False)
    #print("Loading:")
    #pp.pprint(allSettings)

    if "viewSettings" in allSettings:
        global viewSettings
        viewSettings = allSettings["viewSettings"]

        for cat, name, default in [
            ("Tree", "iconSize", 24),   # Added in 0.6.0
            ]:
            if not name in viewSettings[cat]:
                viewSettings[cat][name] = default

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
            "maxWidth": 0,
            "marginsLR": 0,
            "marginsTB": 0,
            "backgroundTransparent": False,      # Added in 0.6.0
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
