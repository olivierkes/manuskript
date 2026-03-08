#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.spellchecker.abstractSpellchecker import AbstractSpellchecker


__spellcheckers__ = []


def getSpellcheckers() -> list:
    global __spellcheckers__
    return filter(lambda spellchecker: spellchecker.isValid(), __spellcheckers__)


def registerSpellchecker(spellchecker: AbstractSpellchecker) -> bool:
    global __spellcheckers__

    if not spellchecker.isValid():
        return False
    
    if spellchecker in __spellcheckers__:
        return False
    
    __spellcheckers__.append(spellchecker)
    return True


def unregisterSpellchecker(spellchecker: AbstractSpellchecker) -> bool:
    global __spellcheckers__

    if not spellchecker in __spellcheckers__:
        return False
    
    __spellcheckers__.remove(spellchecker)
    return True
