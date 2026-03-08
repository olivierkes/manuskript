#!/usr/bin/env python
# --!-- coding: utf8 --!--

from functools import reduce

from manuskript.converter import AbstractConverter, registerConverter, unregisterConverter
from manuskript.exporter import AbstractExporter, registerExporter, unregisterExporter
from manuskript.plugin.component import PluginComponent
from manuskript.spellchecker import AbstractSpellchecker, registerSpellchecker, unregisterSpellchecker
from manuskript.util import profileTime


class AbstractPlugin:

    def __init__(self):
        self.converters: list[AbstractConverter] = []
        self.exporters: list[AbstractExporter] = []
        self.spellcheckers: list[AbstractSpellchecker] = []
        self.loaded: list = [False for c in PluginComponent]
    
    def getName(self) -> str:
        return self.__class__.__name__
    
    def getDescription(self) -> str|None:
        return None
    
    def isValid(self) -> bool:
        return reduce(lambda x, y: x and y, self.loaded)
    
    def registerConverter(self, converter_cls) -> bool:
        try:
            if not issubclass(converter_cls, AbstractConverter):
                return False

            converter = converter_cls()
        except TypeError as e:
            print("PLUGIN ERROR: ( " + self.getName() + " )" + str(e))
            return False
        
        self.converters.append(converter)
        return True
    
    def registerExporter(self, exporter_cls) -> bool:
        try:
            if not issubclass(exporter_cls, AbstractExporter):
                return False

            exporter = exporter_cls()
        except TypeError as e:
            print("PLUGIN ERROR: ( " + self.getName() + " )" + str(e))
            return False
        
        self.exporters.append(exporter)
        return True
    
    def registerSpellchecker(self, spellchecker_cls, language: str) -> bool:
        try:
            if not issubclass(spellchecker_cls, AbstractSpellchecker):
                return False

            spellchecker = spellchecker_cls(language)
        except TypeError as e:
            print("PLUGIN ERROR: ( " + self.getName() + " )" + str(e))
            return False
        
        self.spellcheckers.append(spellchecker)
        return True
    
    def preload(self) -> bool:
        return True
    
    def load(self) -> bool:
        return True
    
    def loadComponent(self, component: PluginComponent) -> bool:
        if component == PluginComponent.REQUIREMENTS:
            return profileTime(self.preload)
        elif component == PluginComponent.CONVERTERS:
            status: bool = True

            for converter in self.converters:
                status = status and registerConverter(converter)
            
            return status
        elif component == PluginComponent.EXPORTERS:
            status: bool = True

            for exporter in self.exporters:
                status = status and registerExporter(exporter)
            
            return status
        elif component == PluginComponent.SPELLCHECKERS:
            status: bool = True

            for spellchecker in self.spellcheckers:
                status = status and registerSpellchecker(spellchecker)
            
            return status
        elif component == PluginComponent.PLUGIN:
            return profileTime(self.load)
        else:
            return False
    
    def unload(self) -> bool:
        return True
    
    def unloadComponent(self, component: PluginComponent) -> bool:
        if component == PluginComponent.REQUIREMENTS:
            self.spellcheckers.clear()
            self.exporters.clear()
            self.converters.clear()
            return True
        elif component == PluginComponent.CONVERTERS:
            status: bool = True

            for converter in self.converters:
                status = status and unregisterConverter(converter)
            
            return status
        elif component == PluginComponent.EXPORTERS:
            status: bool = True

            for exporter in self.exporters:
                status = status and unregisterExporter(exporter)
            
            return status
        elif component == PluginComponent.SPELLCHECKERS:
            status: bool = True

            for spellchecker in self.spellcheckers:
                status = status and unregisterSpellchecker(spellchecker)
            
            return status
        elif component == PluginComponent.PLUGIN:
            return self.unload()
        else:
            return False
