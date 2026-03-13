#!/usr/bin/env python
# --!-- coding: utf8 --!--

import glob
import os

SYMSPELLPY_MIN_VERSION = "6.3.8"
try:
    import symspellpy
    import distutils.version

    if distutils.version.LooseVersion(symspellpy.__version__) < SYMSPELLPY_MIN_VERSION:
        symspellpy = None
    
except ImportError:
    symspellpy = None

from manuskript.plugin import AbstractPlugin
from manuskript.plugin.symspellpy.symSpellchecker import SymSpellchecker


class SymSpellPlugin(AbstractPlugin):

    def __init__(self):
        super().__init__()
    
    def getName(self) -> str:
        return "symspellpy"
    
    def preload(self) -> bool:
        if not symspellpy:
            return False
        
        return True
