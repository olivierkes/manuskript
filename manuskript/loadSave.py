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
    print(zipname)
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
    saveItem(data, mdl)
            
    #print(qApp.tr("Saving to {}.").format(xml))
    if xml:
        ET.ElementTree(root).write(xml, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    else:
        return ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)
   
def saveItem(root, mdl, parent=QModelIndex()):
    for x in range(mdl.rowCount(parent)):
        row = ET.SubElement(root, "row")
        row.attrib["row"] = str(x)
        
        for y in range(mdl.columnCount(parent)):
            col = ET.SubElement(row, "col")
            col.attrib["col"] = str(y)
            if mdl.data(mdl.index(x, y, parent), Qt.DecorationRole) != None:
                color = iconColor(mdl.data(mdl.index(x, y, parent), Qt.DecorationRole)).name(QColor.HexArgb)
                col.attrib["color"] = color if color != "#ff000000" else "#00000000"
            if mdl.data(mdl.index(x, y, parent)) != "":
                col.text = mdl.data(mdl.index(x, y, parent))
            if mdl.hasChildren(mdl.index(x, y, parent)):
                saveItem(col, mdl, mdl.index(x, y, parent))
    
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
    
    #mdl.setVerticalHeaderLabels(vLabels)
    #mdl.setHorizontalHeaderLabels(hLabels)
    
    # Populates with empty items
    for i in enumerate(vLabels):
        row = []
        for r in enumerate(hLabels):
            row.append(QStandardItem())
        mdl.appendRow(row)
    
    #Data
    data = root.find("data")
    loadItem(data, mdl)
            
    return True
    
def loadItem(root, mdl, parent=QModelIndex()):
    for row in root:
        r = int(row.attrib["row"])
        for col in row:
            c = int(col.attrib["col"])
            item = mdl.itemFromIndex(mdl.index(r, c, parent))
            if not item:
                item = QStandardItem()
                mdl.itemFromIndex(parent).setChild(r, c, item)
                
            if col.text: 
                #mdl.setData(mdl.index(r, c, parent), col.text)
                item.setText(col.text)
                
            if "color" in col.attrib:
                #mdl.itemFromIndex(mdl.index(r, c, parent)).setIcon(iconFromColorString(col.attrib["color"]))
                item.setIcon(iconFromColorString(col.attrib["color"]))
                
            if len(col) != 0:
                #loadItem(col, mdl, mdl.index(r, c, parent))
                loadItem(col, mdl, mdl.indexFromItem(item))