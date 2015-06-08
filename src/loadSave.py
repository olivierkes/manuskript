#!/usr/bin/env python
#--!-- coding: utf8 --!--
 



from qt import *

from lxml import etree as ET

def saveStandardItemModelXML(mdl, xml):
    root = ET.Element("model")
    
    # Header
    header = ET.SubElement(root, "header")
    vHeader = ET.SubElement(header, "vertical")
    for x in range(mdl.rowCount()):
        vH = ET.SubElement(vHeader, "label")
        vH.attrib["row"] = str(x)
        vH.attrib["text"] = str(mdl.headerData(x, Qt.Vertical))
    
    hHeader = ET.SubElement(header, "horizontal")
    for y in range(mdl.columnCount()):
        hH = ET.SubElement(hHeader, "label")
        hH.attrib["row"] = str(y)
        hH.attrib["text"] = str(mdl.headerData(y, Qt.Horizontal))
    
    # Data
    data = ET.SubElement(root, "data")
    
    for x in range(mdl.rowCount()):
        row = ET.SubElement(data, "row")
        row.attrib["row"] = str(x)
        
        for y in range(mdl.columnCount()):
            col = ET.SubElement(row, "col")
            col.attrib["col"] = str(y)
            if mdl.data(mdl.index(x, y)) != "":
                col.text = mdl.data(mdl.index(x, y))
            
    print(qApp.tr("Saving to {}.").format(xml))
    ET.ElementTree(root).write(xml, encoding="UTF-8", xml_declaration=True, pretty_print=True)
   
    
def loadStandardItemModelXML(mdl, xml):
    
    
    print(qApp.tr("Loading {}... ").format(xml), end="")
    
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
    
    #print(root.find("header").find("vertical").text)
    
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