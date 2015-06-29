#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
import re


def infoForRef(ref):
    match = re.fullmatch("::(\w):(\d+?)::", ref)
    if match:
        _type = match.group(1)
        _ref = match.group(2)
        
        if _type == "T":
            m = mainWindow().mdlOutline
            idx = m.getIndexByID(_ref)
            
            if not idx.isValid():
                return qApp.translate("references", "Unknown reference: {}.").format(ref)
            
            item = idx.internalPointer()
            
            text = "<h1>{}</h1>".format(item.title())
            text += "<b>Path:</b> {}<br>".format(item.path())
            ss = item.data(Outline.summarySentance.value)
            if ss:
                text += "\n<b>Short summary:</b> {}<br>".format(ss)
                
            ls = item.data(Outline.summaryFull.value)
            if ls:
                text += "\n<b>Long summary:</b> {}<br>".format(ls)
            
            return text
        
        elif _type == "C":
            m = mainWindow().mdlPersos
            name = m.item(int(_ref), Perso.name.value).text()
            return "<h1>{}</h1>".format(name)
            
    else:
        return qApp.translate("references", "Unknown reference: {}.").format(ref)
    
    
def openReference(ref):
    match = re.fullmatch("::(\w):(\d+?)::", ref)
    if match:
        _type = match.group(1)
        _ref = match.group(2)
        
        if _type == "C":
            mw = mainWindow()
            
            for i in range(mw.mdlPersos.rowCount()):
                if mw.mdlPersos.ID(i) == _ref:
                    mw.tabMain.setCurrentIndex(2)
                    item = mw.lstPersos.getItemByID(_ref)
                    mw.lstPersos.setCurrentItem(item)
                    return True
                
            print("Ref not found")
            return False
        
        elif _type == "T":
            
            mw = mainWindow()
            index = mw.mdlOutline.getIndexByID(_ref)
            
            if index.isValid():
                mw.mainEditor.setCurrentModelIndex(index, newTab=True)
                return True
            else:
                print("Ref not found")
                return False
        
        print("Ref not implemented")
        return False