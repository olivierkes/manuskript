#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
from exporter.basic import basicExporter

class odtExporter(basicExporter):
    
    requires = ["filename"]
    
    def __init__(self):
        pass
    
    def doCompile(self, filename):
        mw = mainWindow()
        root = mw.mdlOutline.rootItem
        
        doc = QTextDocument()
        cursor = QTextCursor(doc)
        
        
        def appendItem(item):
            if item.isFolder():
                
                cursor.setPosition(doc.characterCount() - 1)
                title = "<h{l}>{t}</h{l}><br>\n".format(
                    l = str(item.level() + 1),
                    t = item.title())
                cursor.insertHtml(title)
                
                for c in item.children():
                    appendItem(c)
            
            else:
                text = self.formatText(item.text(), item.type())
                cursor.setPosition(doc.characterCount() - 1)
                cursor.insertHtml(text)
                
        for c in root.children():
            appendItem(c)
            
        dw = QTextDocumentWriter(filename, "odt")
        dw.write(doc)
            
    def formatText(self, text, _type):
        
        if not text:
            return text
        
        if _type == "t2t":
            text = self.runT2T(text)
        
        elif _type == "txt":
            text = text.replace("\n", "<br>")
        
        elif _type == "html":
            text = self.htmlBody(text)
        
        return text + "<br>"
