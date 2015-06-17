#!/usr/bin/env python
#--!-- coding: utf8 --!--

from qt import *
from functions import *
from lxml import etree as ET
import zipfile
try:
    import zlib # Used with zipfile for compression
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

def saveFilesToZip(files, zipname):
    """Saves given files to zipname.
    files is actually a list of (content, filename)."""
    
    zf = zipfile.ZipFile(zipname, mode="w")
    
    for content, filename in files:
        zf.writestr(filename, content, compress_type=compression)
    
    zf.close()
    
def loadFilesFromZip(zipname):
    """Returns the content of zipfile as a dict of filename:content."""
    zf = zipfile.ZipFile(zipname)
    files = {}
    for f in zf.namelist():
        files[f] = zf.read(f)
    return files
    
def saveStandardItemModelXML(mdl, xml=None):
    """Saves the given QStandardItemModel to XML.
    If xml (filename) is given, saves to xml. Otherwise returns as string."""
    
    root = ET.Element("model")
    root.attrib["version"] = qApp.applicationVersion()
    
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
            if mdl.data(mdl.index(x, y), Qt.DecorationRole) != None:
                color = iconColor(mdl.data(mdl.index(x, y), Qt.DecorationRole)).name(QColor.HexArgb)
                col.attrib["color"] = color if color != "#ff000000" else "#00000000"
            if mdl.data(mdl.index(x, y)) != "":
                col.text = mdl.data(mdl.index(x, y))
            
    #print(qApp.tr("Saving to {}.").format(xml))
    if xml:
        ET.ElementTree(root).write(xml, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    else:
        return ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)
   
    
def loadStandardItemModelXML(mdl, xml, fromString=False):
    """Load data to a QStandardItemModel mdl from xml.
    By default xml is a filename. If fromString=True, xml is a string containg the data."""
    
    #print(qApp.tr("Loading {}... ").format(xml), end="")
    
    if not fromString:
        try:
            tree = ET.parse(xml)
        except:
            print("Failed.")
            return
    else:
        root = ET.fromstring(xml)
    
    #root = tree.getroot()
    
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
            if "color" in col.attrib:
                mdl.item(r, c).setIcon(iconFromColorString(col.attrib["color"]))
            
    #print("OK")