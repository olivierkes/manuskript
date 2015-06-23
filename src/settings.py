# -*- coding: utf-8 -*-

import pickle
import pprint
from enums import *

viewSettings = {
    "Tree": {
        "Icon": "Nothing",
        "Text": "Compile",
        "Background": "Nothing",
        "InfoFolder": "Nothing",
        "InfoText": "Nothing",
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
    
spellcheck = False
dict = None
corkSizeFactor = 100
folderView = "cork"
lastTab = 0
lastIndex = ""
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
    "image": ""
        }

fullScreenTheme = "spacedreams"

def save(filename=None):
    
    global spellcheck, dict, corkSliderFactor, viewSettings, corkSizeFactor, folderView, lastTab, lastIndex, \
           autoSave, autoSaveDelay, saveOnQuit, autoSaveNoChanges, autoSaveNoChangesDelay, outlineViewColumns, \
           corkBackground, fullScreenTheme
    
    allSettings = {
        "viewSettings": viewSettings,
        "dict": dict,
        "spellcheck": spellcheck,
        "corkSizeFactor": corkSizeFactor,
        "folderView": folderView,
        "lastTab": lastTab,
        "lastIndex": lastIndex,
        "autoSave":autoSave,
        "autoSaveDelay":autoSaveDelay,
        "saveOnQuit":saveOnQuit,
        "autoSaveNoChanges":autoSaveNoChanges,
        "autoSaveNoChangesDelay":autoSaveNoChangesDelay,
        "outlineViewColumns":outlineViewColumns,
        "corkBackground":corkBackground,
        "fullScreenTheme":fullScreenTheme,
        }
    
    #pp=pprint.PrettyPrinter(indent=4, compact=False)
    #print("Saving:")
    #pp.pprint(allSettings)
    
    if filename:
        f = open(filename, "wb")
        pickle.dump(allSettings, f)
    else:
        return pickle.dumps(allSettings)
    
def load(string, fromString=False):
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
        allSettings = pickle.loads(string)
    
    #pp=pprint.PrettyPrinter(indent=4, compact=False)
    #print("Loading:")
    #pp.pprint(allSettings)
    
    if "viewSettings" in allSettings:
        global viewSettings
        viewSettings = allSettings["viewSettings"]
        
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
        
    if "lastIndex" in allSettings:
        global lastIndex
        lastIndex = allSettings["lastIndex"]
        
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
        
    if "fullScreenTheme" in allSettings:
        global fullScreenTheme
        fullScreenTheme = allSettings["fullScreenTheme"]
        