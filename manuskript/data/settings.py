#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.io.jsonFile import JsonFile


class Settings:

    def __init__(self, path, initDefault: bool = True):
        self.file = JsonFile(os.path.join(path, "settings.txt"))
        self.properties = dict()

        if initDefault:
            Settings.loadDefaultSettings(self)

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
        self.properties = self.file.load()

    def save(self):
        self.file.save(self.properties)
