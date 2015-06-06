#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *
from enums import *
from ui.editors.t2tHighlighter import *
try:
    import enchant
except ImportError:
    enchant = None
    
class customTextEdit(QTextEdit):
    
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
        
        self.defaultFontPointSize = 9
        self.highlightWord = ""
        self.highligtCS = False
        
        self.highlighter = t2tHighlighter(self)
            
        # Spellchecking
        if enchant:
            self.dict = enchant.Dict("fr_CH")
            self.spellcheck = True
        else:
            self.spellcheck = False