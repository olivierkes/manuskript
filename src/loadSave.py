#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *

from lxml import etree as ET

def saveStandardItemModelXML(mdl, xml):
    root = ET.Element("model")
    
    # Header
    header = ET.SubElement(root, "header")
    vHeader = ET.SubElement(header, "vertical")
    for x in range(mdl.rowCount()):
        vH = ET.SubElement(vHeader, "label")
        vH.attrib["row"] = unicode(x)
        vH.attrib["text"] = unicode(mdl.headerData(x, Qt.Vertical).toString())
    
    hHeader = ET.SubElement(header, "horizontal")
    for y in range(mdl.columnCount()):
        hH = ET.SubElement(hHeader, "label")
        hH.attrib["row"] = unicode(y)
        hH.attrib["text"] = unicode(mdl.headerData(y, Qt.Horizontal).toString())
    
    # Data
    data = ET.SubElement(root, "data")
    
    for x in range(mdl.rowCount()):
        row = ET.SubElement(data, "row")
        row.attrib["row"] = unicode(x)
        
        for y in range(mdl.columnCount()):
            col = ET.SubElement(row, "col")
            col.attrib["col"] = unicode(y)
            col.text = unicode(mdl.data(mdl.index(x, y)).toString())
            
    print("Saving to {}.".format(xml))
    ET.ElementTree(root).write(xml, encoding="UTF-8",xml_declaration=True, pretty_print=True)
   
    
def loadStandardItemModelXML(mdl, xml):
    
    
    print("Loading {}... ".format(xml), end="")
    
    try:
        tree = ET.parse(xml)
    except:
        print("Failed.")
        return
    
    root = tree.getroot()
    
    #Header
    hLabels = []
    vLabels = []
    for l in root.find("header").find("horizontal").findall("label"):
        hLabels.append(l.attrib["text"])
    for l in root.find("header").find("vertical").findall("label"):
        vLabels.append(l.attrib["text"])
    
    mdl.setVerticalHeaderLabels(vLabels)
    mdl.setHorizontalHeaderLabels(hLabels)
    
    #Data
    for row in root.find("data").iter("row"):
        r = int(row.attrib["row"])
        for col in row.iter("col"):
            c = int(col.attrib["col"])
            if col.text: 
                mdl.setData(mdl.index(r, c), col.text)

    print("OK")