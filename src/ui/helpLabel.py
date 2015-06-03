#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from qt import *

class helpLabel(QLabel):
    
    def __init__(self, text=None, parent=None):
        QLabel.__init__(self, text, parent)
        
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        
        self.setStatusTip("Infobulle: Si tu me trouve dérengant, tu peux me cacher via le menu Aide.")
        
        self.setStyleSheet("""
            QLabel {
                background-color:lightYellow;
                border:1px solid lightGray;
                border-radius: 10px;
                margin: 3px;
                padding:10px;
                color:gray;
            }""")