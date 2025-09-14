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

tooltipStyle = {
    "useSystemDefaultsForTooltips": True,
    "textColor": "#000000",
    "backgroundColor": "#ffffdc",
    "borderColor": "#767676"
}

aiFeatures = {
    "claudeAPIKey": "",
    "narrativeGraphMemory": False,
    "adaptiveVoiceStyle": False
}

# -------------------------
# AI Hook System
# -------------------------
ai_hooks = {
    "before_save": [],
    "after_save": [],
    "before_load": [],
    "after_load": [],
    "text_changed": [],
    "character_changed": [],
    "outline_changed": [],
    "plot_changed": []
}

def register_hook(event: str, callback, feature_key=None, priority=10):
    """
    Register a callback function for a specific AI hook event.
    
    Args:
        event: The hook event name (e.g., 'before_save', 'after_save', etc.)
        callback: The function to call when the event occurs
        feature_key: Optional AI feature key - callback only runs if this feature is enabled
        priority: Execution priority (lower numbers run first, default 10)
    
    Raises:
        ValueError: If event is invalid or callback is not callable
    """
    if event not in ai_hooks:
        raise ValueError(f"Invalid event: {event}")
    
    if not callable(callback):
        raise ValueError(f"Callback must be callable: {callback}")
    
    hook_entry = {
        "callback": callback,
        "feature_key": feature_key,
        "priority": priority
    }
    
    ai_hooks[event].append(hook_entry)
    
    # Sort by priority after adding
    ai_hooks[event].sort(key=lambda x: x["priority"])
    
    feature_msg = f" (requires '{feature_key}')" if feature_key else ""
    LOGGER.info(f"Registered hook for event: {event}{feature_msg}")

def unregister_hook(event: str, callback):
    """
    Unregister a callback function from a specific AI hook event.
    
    Args:
        event: The hook event name
        callback: The function to remove
    """
    if event in ai_hooks:
        # Find and remove the hook entry with matching callback
        ai_hooks[event] = [h for h in ai_hooks[event] if h["callback"] != callback]
        LOGGER.info(f"Unregistered hook for event: {event}")

def trigger_hook(event: str, *args, async_mode=False, **kwargs):
    """
    Trigger all callbacks registered to the given event.
    Only runs callbacks whose AI feature is enabled (if feature_key is set).
    
    Args:
        event: The hook event name
        *args: Positional arguments to pass to callbacks
        async_mode: If True, run CPU-heavy hooks in background threads
        **kwargs: Keyword arguments to pass to callbacks
    
    Returns:
        bool: True if all hooks executed successfully, False if any failed
    """
    LOGGER.info(f"trigger_hook called for event: {event}, async_mode: {async_mode}")
    
    if event not in ai_hooks:
        LOGGER.warning(f"Unknown hook event: {event}")
        return False
    
    # Use async execution if requested
    if async_mode:
        return _trigger_hook_async(event, *args, **kwargs)
    
    success = True
    LOGGER.debug(f"Processing {len(ai_hooks[event])} hooks for event: {event}")
    LOGGER.debug(f"Current aiFeatures: {aiFeatures}")
    for hook in ai_hooks[event]:
        callback = hook["callback"]
        feature_key = hook.get("feature_key")
        
        try:
            # Only run if no feature_key is set, or if the feature is enabled
            feature_enabled = aiFeatures.get(feature_key, False) if feature_key else True
            LOGGER.debug(f"Hook {callback.__name__} for event {event}: feature_key={feature_key}, enabled={feature_enabled}")
            if feature_key is None or feature_enabled:
                # Check if callback is marked as CPU-heavy (avoid Mock issues)
                is_cpu_heavy = False
                if hasattr(callback, '_cpu_heavy'):
                    # Only consider it cpu_heavy if it's explicitly set to True
                    # This avoids Mock objects which return Mock for any attribute
                    cpu_heavy_attr = getattr(callback, '_cpu_heavy')
                    is_cpu_heavy = cpu_heavy_attr is True or cpu_heavy_attr == True
                
                if is_cpu_heavy:
                    # Run in background thread
                    success &= _run_callback_async(callback, *args, **kwargs)
                else:
                    # Run synchronously
                    callback(*args, **kwargs)
        except Exception as e:
            callback_name = getattr(callback, "__name__", str(callback))
            LOGGER.error(f"[AI Hook Error] {event} callback {callback_name} failed: {e}")
            success = False
    
    return success

def _trigger_hook_async(event: str, *args, **kwargs):
    """
    Internal function to handle async hook triggering.
    Uses late import to avoid circular dependencies.
    """
    try:
        from manuskript.ai.async_worker import trigger_hook_async
        trigger_hook_async(event, *args, **kwargs)
        return True
    except ImportError as e:
        LOGGER.warning(f"Async worker not available, running hooks synchronously: {e}")
        # Fall back to synchronous execution
        return trigger_hook(event, *args, async_mode=False, **kwargs)

def _run_callback_async(callback, *args, **kwargs):
    """
    Internal function to run a single callback asynchronously.
    Uses late import to avoid circular dependencies.
    """
    try:
        from manuskript.ai.async_worker import run_async
        run_async(callback, *args, **kwargs)
        return True
    except ImportError as e:
        LOGGER.warning(f"Async worker not available, running callback synchronously: {e}")
        # Fall back to synchronous execution
        try:
            callback(*args, **kwargs)
            return True
        except Exception as ex:
            callback_name = getattr(callback, "__name__", str(callback))
            LOGGER.error(f"[AI Hook Error] Callback {callback_name} failed: {ex}")
            return False

def clear_hooks(event: str = None):
    """
    Clear all callbacks for a specific event or all events.
    
    Args:
        event: The specific event to clear (None clears all events)
    """
    if event:
        if event in ai_hooks:
            ai_hooks[event].clear()
            LOGGER.info(f"Cleared all hooks for event: {event}")
    else:
        for evt in ai_hooks:
            ai_hooks[evt].clear()
        LOGGER.info("Cleared all AI hooks")

viewMode = "fiction"  # simple, fiction
saveToZip = False
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

def applyTooltipStyle():
    """
    Apply tooltip styling to the application if system defaults are disabled.
    """
    if not tooltipStyle["useSystemDefaultsForTooltips"]:
        from PyQt5.QtWidgets import qApp
        qApp.setStyleSheet(f"QToolTip {{ color: {tooltipStyle['textColor']}; background-color: {tooltipStyle['backgroundColor']}; border: 1px solid {tooltipStyle['borderColor']}; }}")

def save(filename=None, protocol=None):

    global spellcheck, dict, corkSliderFactor, viewSettings, corkSizeFactor, folderView, lastTab, openIndexes, \
           progressChars, autoSave, autoSaveDelay, saveOnQuit, autoSaveNoChanges, autoSaveNoChangesDelay, outlineViewColumns, \
           corkBackground, corkStyle, fullScreenTheme, defaultTextType, textEditor, revisions, frequencyAnalyzer, viewMode, \
           saveToZip, dontShowDeleteWarning, fullscreenSettings, tooltipStyle, aiFeatures

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
        "tooltipStyle": tooltipStyle,
        "aiFeatures": aiFeatures,
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

    if "tooltipStyle" in allSettings:
        global tooltipStyle
        loaded_tooltip_style = allSettings["tooltipStyle"]
        # Add missing keys with defaults
        if "useSystemDefaultsForTooltips" not in loaded_tooltip_style:
            loaded_tooltip_style["useSystemDefaultsForTooltips"] = True
        tooltipStyle = loaded_tooltip_style
    
    if "aiFeatures" in allSettings:
        global aiFeatures
        loaded_ai_features = allSettings["aiFeatures"]
        # Add missing keys with defaults
        if "claudeAPIKey" not in loaded_ai_features:
            loaded_ai_features["claudeAPIKey"] = ""
        if "narrativeGraphMemory" not in loaded_ai_features:
            loaded_ai_features["narrativeGraphMemory"] = False
        if "adaptiveVoiceStyle" not in loaded_ai_features:
            loaded_ai_features["adaptiveVoiceStyle"] = False
        aiFeatures = loaded_ai_features
