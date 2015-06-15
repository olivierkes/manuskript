# -*- coding: utf-8 -*-

import pickle
import pprint

viewSettings = {
    "Tree": {
        "Icon": "Nothing",
        "Text": "Compile",
        "Background": "Nothing",
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

def save(filename):
    
    global spellcheck, dict, corkSliderFactor, viewSettings, corkSizeFactor, folderView
    
    allSettings = {
        "viewSettings": viewSettings,
        "dict": dict,
        "spellcheck": spellcheck,
        "corkSizeFactor": corkSizeFactor,
        "folderView": folderView
        }
    
    #pp=pprint.PrettyPrinter(indent=4, compact=False)
    #print("Saving:")
    #pp.pprint(allSettings)
    
    f = open(filename, "wb")
    pickle.dump(allSettings, f)
    
def load(filename):
    try:
        global allSettings
        
        f = open(filename, "rb")
        allSettings = pickle.load(f)
        
    except:
        print("{} doesn't exist, cannot load settings.".format(filename))
        return
    
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
        
    
    