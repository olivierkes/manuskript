#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
from exporter.basic import basicExporter

import sys, os
sys.path.append(os.path.join(appPath(), "libs"))

from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties
from odf.text import H, P, Span


class odtExporter(basicExporter):
    
    requires = ["filename"]
    
    def __init__(self):
        pass
    
    def doCompile(self, filename):
        mw = mainWindow()
        root = mw.mdlOutline.rootItem
        
        doc = OpenDocumentText()
        
        def appendItem(item):
            if item.isFolder():
                
                self.addHeading(item.title(), item.level() + 1, doc)
                
                for c in item.children():
                    appendItem(c)
            
            else:
                text = self.formatText(item.text(), item.type())
                if text:
                    for l in text.split("\n"):
                        self.addParagraph(l, doc)
                
        for c in root.children():
            appendItem(c)
            
        doc.save(filename)
            
    def formatText(self, text, _type):
        
        if not text:
            return text
        
        #if _type == "t2t":
            #text = self.runT2T(text)
        
        #elif _type == "txt":
            #text = text.replace("\n", "<br>")
        
        elif _type == "html":
            doc = QTextDocument()
            doc.setHtml(text)
            text = doc.toPlainText()
            #text = self.htmlBody(text)
        
        return text
    
    def addHeading(self, text, level, doc):
        doc.text.addElement(H(outlinelevel=int(level), text=text))
        return doc
    
    def addParagraph(self, text, doc):
        p = P(stylename="Text Body", text=text)
        doc.text.addElement(p)
        return doc