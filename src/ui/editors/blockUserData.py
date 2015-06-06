#!/usr/bin/python
# -*- coding: utf8 -*-

from qt import *


class blockUserData (QTextBlockUserData):

    @staticmethod
    def getUserData(block):
        "Returns userData if it exists, or a blank one."
        data = block.userData()
        if data is None:
            data = blockUserData()
        return data

    @staticmethod
    def getUserState(block):
        "Returns the block state."
        state = block.userState()
        while state >= 100:
            state -= 100  # +100 means in a list
        return state

    def __init__(self):
        QTextBlockUserData.__init__(self)
        self._listLevel = 0
        self._leadingSpaces = 0
        self._emptyLinesBefore = 0
        self._listSymbol = ""

    def isList(self):
        return self._listLevel > 0

    def listLevel(self):
        return self._listLevel

    def setListLevel(self, level):
        self._listLevel = level

    def listSymbol(self):
        return self._listSymbol

    def setListSymbol(self, s):
        self._listSymbol = s

    def leadingSpaces(self):
        return self._leadingSpaces

    def setLeadingSpaces(self, n):
        self._leadingSpaces = n

    def emptyLinesBefore(self):
        return self._emptyLinesBefore

    def setEmptyLinesBefore(self, n):
        self._emptyLinesBefore = n

    def text(self):
        return str(self.listLevel()) + "|" + str(self.leadingSpaces()) + "|" + str(self.emptyLinesBefore())

    def __eq__(self, b):
        return self._listLevel == b._listLevel and \
               self._leadingSpaces == b._leadingSpaces and \
               self._emptyLinesBefore == b._emptyLinesBefore

    def __ne__(self, b):
        return not self == b
