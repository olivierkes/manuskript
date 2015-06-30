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
            
            #<p><b>Status:</b> {status}</p>
            #<p><b>Label:</b> {label}</p>
            
            if item.POV():
                POV = "<a href='{ref}'>{text}</a>".format(
                    ref="::C:{}::".format(item.POV()),
                    text=mainWindow().mdlPersos.getPersoNameByID(item.POV()))
            else:
                POV = qApp.translate("references", "None")
            
            path = item.pathID()
            pathStr = []
            for _id, title in path:
                pathStr.append("<a href='{ref}'>{text}</a>".format(
                    ref="::T:{}::".format(_id),
                    text=title))
            path = " > ".join(pathStr)
            
            text = """<h1>{title}</h1>
            <p><b>Path:</b> {path}</p>
            <p><b>Stats:</b> {stats}</p>
            <p><b>POV:</b> {POV}</p>
            <p><b>Short summary:</b> {ss}</p>
            <p><b>Long summary:</b> {ls}</p>
            <p><b>Notes:</b> {notes}</p>
            """.format(
                title=item.title(),
                path=path,
                stats=item.stats(),
                POV=POV,
                ss=item.data(Outline.summarySentance.value).replace("\n", "<br>"),
                ls=item.data(Outline.summaryFull.value).replace("\n", "<br>"),
                notes=linkifyAllRefs(item.data(Outline.notes.value)).replace("\n", "<br>"))
            
            return text
        
        elif _type == "C":
            m = mainWindow().mdlPersos
            name = m.item(int(_ref), Perso.name.value).text()
            return "<h1>{}</h1>".format(name)
            
    else:
        return qApp.translate("references", "Unknown reference: {}.").format(ref)
    
def refToLink(ref):
    match = re.fullmatch("::(\w):(\d+?)::", ref)
    if match:
        _type = match.group(1)
        _ref = match.group(2)
        text = ""
        if _type == "T":
            m = mainWindow().mdlOutline
            idx = m.getIndexByID(_ref)
            if idx.isValid():
                item = idx.internalPointer()
                text = item.title()
            
        elif _type == "C":
            m = mainWindow().mdlPersos
            text = m.item(int(_ref), Perso.name.value).text()
            
        if text:
            return "<a href='{ref}'>{text}</a>".format(
                    ref=ref,
                    text=text)
        else:
            return ref
    
def linkifyAllRefs(text):
    return re.sub(r"::(\w):(\d+?)::", lambda m: refToLink(m.group(0)), text)
    
def tooltipForRef(ref):
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
            
            tooltip = qApp.translate("references", "Text: <b>{}</b>").format(item.title())
            tooltip += "<br><i>{}</i>".format(item.path())
            
            return tooltip
        
        elif _type == "C":
            m = mainWindow().mdlPersos
            name = m.item(int(_ref), Perso.name.value).text()
            return qApp.translate("references", "Character: <b>{}</b>").format(name)
            
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