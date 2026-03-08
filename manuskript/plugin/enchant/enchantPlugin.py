#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import enchant
except ModuleNotFoundError:
    enchant = None

from manuskript.plugin import AbstractPlugin
from manuskript.plugin.enchant.enchantSpellchecker import EnchantSpellchecker


class EnchantPlugin(AbstractPlugin):

    def __init__(self):
        super().__init__()
    
    def getName(self) -> str:
        return "PyEnchant"
    
    def preload(self) -> bool:
        if not enchant:
            return False
        
        for d in enchant.list_dicts():
            self.registerSpellchecker(EnchantSpellchecker, d[0])
        
        return True
