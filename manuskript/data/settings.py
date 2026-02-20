#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.data.abstractData import AbstractData
from manuskript.io.jsonFile import JsonFile

class SettingsKeys:

    AUTO_SAVE = "autoSave"
    AUTO_SAVE_DELAY = "autoSaveDelay"
    AUTO_SAVE_NO_CHANGES = "autoSaveNoChanges"
    AUTO_SAVE_NO_CHANGES_DELAY = "autoSaveNoChangesDelay"
    CORK_SIZE_FACTOR = "corkSizeFactor"
    CORK_STYLE = "corkStyle"
    COUNT_SPACES = "countSpaces"
    DEFAULT_TEXT_TYPE = "defaultTextType"
    DICT = "dict"
    DONT_SHOW_DELETE_WARNING = "dontShowDeleteWarning"
    FOLDER_VIEW = "folderView"
    FULL_SCREEN_THEME = "fullScreenTheme"
    LAST_TAB = "lastTab"
    OPEN_INDEXES = "openIndexes"
    OUTLINE_VIEW_COLUMNS = "outlineViewColumns"
    SAVE_ON_QUIT = "saveOnQuit"
    SAVE_TO_ZIP = "saveToZip"
    SPELLCHECK = "spellcheck"
    VIEW_MODE = "viewMode"

    class CorkBackground:
        COLOR = "corkBackground.color"
        IMAGE = "corkBackground.image"

    class FrequencyAnalyzer:
        PHRASE_MAX = "frequencyAnalyzer.phraseMax"
        PHRASE_MIN = "frequencyAnalyzer.phraseMin"
        WORD_EXCLUDE = "frequencyAnalyzer.wordExclude"
        WORD_MIN = "frequencyAnalyzer.wordMin"

    class Revisions:
        KEEP = "revisions.keep"
        SMARTREMOVE = "revisions.smartremove"

        class Rules:
            DELAY_PER_MINUTE = "revisions.rules.600"
            DELAY_PER_10_MINUTES = "revisions.rules.3600"
            DELAY_PER_HOUR = "revisions.rules.86400"
            DELAY_PER_DAY = "revisions.rules.2592000"
            DELAY_PER_WEEK = "revisions.rules.null"
    class TextEditor:
        ALWAYS_CENTER = "textEditor.alwaysCenter"
        BACKGROUND = "textEditor.background"
        BACKGROUND_TRANSPARENT = "textEditor.backgroundTransparent"
        CURSOR_NOT_BLINKING = "textEditor.cursorNotBlinking"
        CURSOR_WIDTH = "textEditor.cursorWidth"
        FOCUS_MODE = "textEditor.focusMode"
        FONT = "textEditor.font"
        FONT_COLOR = "textEditor.fontColor"
        INDENT = "textEditor.indent"
        LINE_SPACING = "textEditor.lineSpacing"
        MARGINS_LR = "textEditor.marginsLR"
        MARGINS_TB = "textEditor.marginsTB"
        MAX_WIDTH = "textEditor.maxWidth"
        MISSPELLED = "textEditor.misspelled"
        SPACING_ABOVE = "textEditor.spacingAbove"
        SPACING_BELOW = "textEditor.spacingBelow"
        TAB_WIDTH = "textEditor.tabWidth"
        TEXT_ALIGNMENT = "textEditor.textAlignment"

    class ViewSettings:
        class Cork:
            BACKGROUND = "viewSettings.Cork.Background"
            BORDER = "viewSettings.Cork.Border"
            CORNER = "viewSettings.Cork.Corner"
            ICON = "viewSettings.Cork.Icon"
            TEXT = "viewSettings.Cork.Text"

        class Outline:
            BACKGROUND = "viewSettings.Outline.Background"
            ICON = "viewSettings.Outline.Icon"
            TEXT = "viewSettings.Outline.Text"

        class Tree:
            BACKGROUND = "viewSettings.Tree.Background"
            ICON = "viewSettings.Tree.Icon"
            INFO_FOLDER = "viewSettings.Tree.InfoFolder"
            INFO_TEXT = "viewSettings.Tree.InfoText"
            TEXT = "viewSettings.Tree.Text"
            ICON_SIZE = "viewSettings.Tree.iconSize"


class Settings(AbstractData):

    def __init__(self, path, initDefault: bool = True):
        AbstractData.__init__(self, os.path.join(path, "settings.txt"))
        self.file = JsonFile(self.dataPath)
        self.properties = dict()

        if initDefault:
            Settings.loadDefaultSettings(self)

    def changePath(self, path: str):
        AbstractData.changePath(self, os.path.join(path, "settings.txt"))
        self.file = JsonFile(self.dataPath)

    def get(self, key: str):
        props = self.properties
        path = key.split(".")        

        for part in path[:-1]:
            props = props.get(part)

        return props.get(path[-1:][0])

    def isEnabled(self, key: str) -> bool:
        return self.properties.get(key, False) is True

    def set(self, key: str, value):
        props = self.properties
        path = key.split(".")

        for part in path[:-1]:
            props = props.get(part)

        props[path[-1:][0]] = value

    def __iter__(self):
        return self.properties.__iter__()

    @classmethod
    def loadDefaultSettings(cls, settings):
        settings.properties = {
            'autoSave': False,
            'autoSaveDelay': 5,
            'autoSaveNoChanges': True,
            'autoSaveNoChangesDelay': 5,

            'corkBackground': {
                'color': '#926239',
                'image': 'writingdesk.jpg'
            },

            'corkSizeFactor': 84,
            'corkStyle': 'new',

            'defaultTextType': 'md',
            'dict': 'en_US',
            'dontShowDeleteWarning': False,
            'folderView': 'cork',
            'frequencyAnalyzer': {
                'phraseMax': 5,
                'phraseMin': 2,
                'wordExclude': 'a, and, or',
                'wordMin': 1
            },

            'fullScreenTheme': 'gentleblues',
            'lastTab': 6,
            'openIndexes': [None],
            'outlineViewColumns': [0, 8, 9, 11, 12, 13, 7],

            'revisions': {
                'keep': True,
                'rules': {
                    '2592000': 86400,
                    '3600': 600,
                    '600': 60,
                    '86400': 3600,
                    'null': 604800},
                'smartremove': True
            },

            'saveOnQuit': True,
            'saveToZip': False,

            'spellcheck': False,

            'textEditor': {
                'background': '#fff',
                'backgroundTransparent': False,
                'cursorNotBlinking': False,
                'cursorWidth': 1,
                'font': 'DejaVu Sans,10,-1,5,50,0,0,0,0,0',
                'fontColor': '#000',
                'indent': True,
                'lineSpacing': 100,
                'marginsLR': 0,
                'marginsTB': 0,
                'maxWidth': 0,
                'misspelled': '#F00',
                'spacingAbove': 5,
                'spacingBelow': 5,
                'tabWidth': 20,
                'textAlignment': 0
            },

            'viewMode': 'fiction',
            'viewSettings': {
                'Cork': {
                    'Background': 'Nothing',
                    'Border': 'Nothing',
                    'Corner': 'Label',
                    'Icon': 'Nothing',
                    'Text': 'Nothing'
                },

                'Outline': {
                    'Background': 'Nothing',
                    'Icon': 'Nothing',
                    'Text': 'Compile'
                },

                'Tree': {
                    'Background': 'Nothing',
                    'Icon': 'Nothing',
                    'InfoFolder': 'Summary',
                    'InfoText': 'Nothing',
                    'Text': 'Compile',
                    'iconSize': 24
                }
            }
        }

    def load(self):
        AbstractData.load(self)

        try:
            self.properties = self.file.load()
        except FileNotFoundError:
            Settings.loadDefaultSettings(self)

        self.complete()

    def save(self):
        AbstractData.save(self)

        self.file.save(self.properties)
        self.complete()
