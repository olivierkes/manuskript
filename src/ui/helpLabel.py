#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *

class helpLabel(QLabel):
    
    def __init__(self, text=None, parent=None):
        QLabel.__init__(self, text, parent)
        
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        
        self.setStatusTip(self.tr("If you don't wanna see me, you can hide me in Help menu."))
        
        self.setStyleSheet("""
            QLabel {
                background-color:lightYellow;
                border:1px solid lightGray;
                border-radius: 10px;
                margin: 3px;
                padding:10px;
                color:gray;
            }""")