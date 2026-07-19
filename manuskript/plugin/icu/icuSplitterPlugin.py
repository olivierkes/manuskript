#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import icu
except ModuleNotFoundError:
    icu = None

from manuskript.plugin import AbstractPlugin
from manuskript.plugin.icu.icuSplitter import ICUSplitter


class ICUSplitterPlugin(AbstractPlugin):

    def __init__(self):
        super().__init__()
    
    def preload(self) -> bool:
        if not icu:
            return False
        
        self.registerSplitter(ICUSplitter)
        return True
