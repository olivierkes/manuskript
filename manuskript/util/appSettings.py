#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from gi.repository import GLib
import os

class AppSettingsKeys(Enum):
    AUTOMATIC_LOAD = ("startup", "automaticLoad", False)
    GENERAL_LANGUAGE = ("preferences", "generalLanguage", "English")
    GENERAL_FONTSIZE = ("preferences", "generalFontSize", 4.0)

    def __init__(self, groupName: str, keyName: str, defaultValue: any):
        self.groupName: str = groupName
        self.keyName: str = keyName
        self.defaultValue: any = defaultValue

class AppSettings:
    _instance = None
    _initialized = False

    automaticLoad: bool
    generalLanguage: str
    generalFontSize: int
    settings: dict[AppSettingsKeys, any]

    keyfileGetters = {
        str: "get_string",
        int: "get_integer",
        bool: "get_boolean",
        float: "get_double"
    }

    keyfileSetters = {
        str: "set_string",
        int: "set_integer",
        bool: "set_boolean",
        float: "set_double"
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        configDir = os.path.join(
            GLib.get_user_config_dir(), "manuskript"
        )

        self.configFile = os.path.join(configDir, "manuskript.ini")
        self.keyfile = GLib.KeyFile()

        if os.path.exists(self.configFile):
            self.keyfile.load_from_file(
                self.configFile,
                GLib.KeyFileFlags.NONE
            )

        self.settings = {}

        for key in AppSettingsKeys:
            self.settings[key] = self._getValue(key.groupName, key.keyName, key.defaultValue)

        self._initialized = True

    def _getValue(self, groupName: str, keyName: str, defaultValue: any):
        if not self.keyfile.has_group(groupName):
            return defaultValue
        
        keys, _ = self.keyfile.get_keys(groupName)
        if not keyName in keys:
            return defaultValue
        
        methodName = self.keyfileGetters[type(defaultValue)]
        getter = getattr(self.keyfile, methodName)
        return getter(groupName, keyName)
    
    def _setValue(self, groupName: str, keyName: str, value: any):
        methodName = self.keyfileSetters[type(value)]
        setter = getattr(self.keyfile, methodName)
        setter(groupName, keyName, value)

    def save(self):
        for key in AppSettingsKeys:
            self._setValue(key.groupName, key.keyName, self.settings[key])

        self.keyfile.save_to_file(self.configFile)

    def getValue(self, key: AppSettingsKeys) -> any:
        return self.settings[key]
    
    def setValue(self, key: AppSettingsKeys, value: any):
        self.settings[key] = value
        self.save()