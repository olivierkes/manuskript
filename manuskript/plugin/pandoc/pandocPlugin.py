#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import pypandoc
except ModuleNotFoundError:
    pypandoc = None

from manuskript.plugin import AbstractPlugin
from manuskript.plugin.pandoc.pandocConverter import PandocConverter


class PandocPlugin(AbstractPlugin):

    def __init__(self):
        super().__init__()
    
    def preload(self) -> bool:
        if not pypandoc:
            return False
        
        self.registerConverter(PandocConverter)
        return True
