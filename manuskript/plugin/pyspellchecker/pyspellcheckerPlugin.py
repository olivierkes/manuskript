#!/usr/bin/env python
# --!-- coding: utf8 --!--

import glob
import os

try:
    import spellchecker as pyspellchecker
except ImportError:
    pyspellchecker = None

from manuskript.plugin import AbstractPlugin
from manuskript.plugin.pyspellchecker.pySpellchecker import PySpellchecker


class PySpellcheckerPlugin(AbstractPlugin):

    def __init__(self):
        super().__init__()
    
    def getName(self) -> str:
        return "pyspellchecker"
    
    def preload(self) -> bool:
        if not pyspellchecker:
            return False
        
        files = glob.glob(os.path.join(pyspellchecker.__path__[0], "resources", "*.json.gz"))
        for file in files:
            self.registerSpellchecker(PySpellchecker, os.path.basename(file)[:-8])
        
        return True
