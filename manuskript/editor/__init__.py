#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.editor.abstractRegioner import AbstractRegioner
from manuskript.editor.abstractSplitter import AbstractSplitter
from manuskript.editor.regexSplitter import RegexSplitter
from manuskript.editor.splitResult import SplitResult, SplitTuple
from manuskript.editor.textRegioner import TextRegioner
from manuskript.editor.textSplitter import TextSplitter


__regioners__ = [
    TextRegioner(),
]

__splitters__ = [
    TextSplitter(),
    RegexSplitter(),
]


def getRegioners() -> list:
    global __regioners__
    return filter(lambda regioner: regioner.isValid(), __regioners__)


def getRegionerByName(name: str) -> AbstractRegioner | None:
    for regioner in getRegioners():
        if regioner.getName() == name:
            return regioner

    return None


def registerRegioner(regioner: AbstractRegioner) -> bool:
    global __regioners__

    if not regioner.isValid():
        return False
    
    if regioner in __regioners__:
        return False
    
    __regioners__.append(regioner)
    return True


def unregisterRegioner(regioner: AbstractRegioner) -> bool:
    global __regioners__

    if not regioner in __regioners__:
        return False
    
    __regioners__.remove(regioner)
    return True


def getSplitters() -> list:
    global __splitters__
    return filter(lambda splitter: splitter.isValid(), __splitters__)


def getSplitterByName(name: str) -> AbstractSplitter | None:
    for splitter in getSplitters():
        if splitter.getName() == name:
            return splitter

    return None


def registerSplitter(splitter: AbstractSplitter) -> bool:
    global __splitters__

    if not splitter.isValid():
        return False
    
    if splitter in __splitters__:
        return False
    
    __splitters__.append(splitter)
    return True


def unregisterSplitter(splitter: AbstractSplitter) -> bool:
    global __splitters__

    if not splitter in __splitters__:
        return False
    
    __splitters__.remove(splitter)
    return True
