#!/usr/bin/env python
# --!-- coding: utf8 --!--

# Version 0 of file saving format.
# Was used at the beginning and up until version XXX when
# it was superseded by Version 1, which is more open and flexible
import os
import zipfile

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QColor, QStandardItem
from PyQt5.QtWidgets import qApp
from lxml import etree as ET

from manuskript import settings
from manuskript.functions import iconColor, iconFromColorString, mainWindow
from manuskript.models.characterModel import Character, CharacterInfo

import logging
LOGGER = logging.getLogger(__name__)

try:
    import zlib  # Used with zipfile for compression

    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

###########################################################################################
# SAVE
###########################################################################################

def saveProject():
    """
    Saves the whole project. Call this function to save the project in Version 0 format.
    """

    files = []
    mw = mainWindow()

    files.append((saveStandardItemModelXML(mw.mdlFlatData),
                  "flatModel.xml"))
    LOGGER.error("File format 0 does not save characters!")
    # files.append((saveStandardItemModelXML(mw.mdlCharacter),
    #               "perso.xml"))
    files.append((saveStandardItemModelXML(mw.mdlWorld),
                  "world.xml"))
    files.append((saveStandardItemModelXML(mw.mdlLabels),
                  "labels.xml"))
    files.append((saveStandardItemModelXML(mw.mdlStatus),
                  "status.xml"))
    files.append((saveStandardItemModelXML(mw.mdlPlots),
                  "plots.xml"))
    files.append((mw.mdlOutline.saveToXML(),
                  "outline.xml"))
    files.append((settings.save(),
                  "settings.pickle"))

    saveFilesToZip(files, mw.currentProject)

def saveFilesToZip(files, zipname):
    """Saves given files to zipname.
    files is actually a list of (content, filename)."""

    zf = zipfile.ZipFile(zipname, mode="w")

    for content, filename in files:
        zf.writestr(filename, content, compress_type=compression)

    zf.close()

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

    # LOGGER.info("Saving to {}.".format(xml))
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

###########################################################################################
# LOAD
###########################################################################################

def loadProject(project):

    files = loadFilesFromZip(project)
    mw = mainWindow()

    errors = []

    if "flatModel.xml" in files:
        loadStandardItemModelXML(mw.mdlFlatData,
                                 files["flatModel.xml"], fromString=True)
    else:
        errors.append("flatModel.xml")

    if "perso.xml" in files:
        loadStandardItemModelXMLForCharacters(mw.mdlCharacter, files["perso.xml"])
    else:
        errors.append("perso.xml")

    if "world.xml" in files:
        loadStandardItemModelXML(mw.mdlWorld,
                                 files["world.xml"], fromString=True)
    else:
        errors.append("world.xml")

    if "labels.xml" in files:
        loadStandardItemModelXML(mw.mdlLabels,
                                 files["labels.xml"], fromString=True)
    else:
        errors.append("labels.xml")

    if "status.xml" in files:
        loadStandardItemModelXML(mw.mdlStatus,
                                 files["status.xml"], fromString=True)
    else:
        errors.append("status.xml")

    if "plots.xml" in files:
        loadStandardItemModelXML(mw.mdlPlots,
                                 files["plots.xml"], fromString=True)
    else:
        errors.append("plots.xml")

    if "outline.xml" in files:
        mw.mdlOutline.loadFromXML(files["outline.xml"], fromString=True)
    else:
        errors.append("outline.xml")

    if "settings.txt" in files:
        settings.load(files["settings.txt"], fromString=True, protocol=0)
    else:
        errors.append("settings.txt")

    if "settings.pickle" in files:
        LOGGER.info("Pickle settings files are no longer supported for security reasons. You can delete it from your data.")

    return errors


def loadFilesFromZip(zipname):
    """Returns the content of zipfile as a dict of filename:content."""
    zf = zipfile.ZipFile(zipname)
    files = {}
    for f in zf.namelist():
        # Some archiving programs (e.g. 7-Zip) also store entries for the directories when
        # creating an archive. We have no use for these entries; skip them entirely.
        if f[-1:] != '/':
            files[os.path.normpath(f)] = zf.read(f)
    return files


def loadStandardItemModelXML(mdl, xml, fromString=False):
    """Load data to a QStandardItemModel mdl from xml.
    By default xml is a filename. If fromString=True, xml is a string containing the data."""

    # LOGGER.info("Loading {}...".format(xml))

    if not fromString:
        try:
            tree = ET.parse(xml)
        except:
            LOGGER.error("Failed to load XML for QStandardItemModel (%s).", xml)
            return
    else:
        root = ET.fromstring(xml)

    # root = tree.getroot()

    # Header
    hLabels = []
    vLabels = []
    for l in root.find("header").find("horizontal").findall("label"):
        hLabels.append(l.attrib["text"])
    for l in root.find("header").find("vertical").findall("label"):
        vLabels.append(l.attrib["text"])

    # LOGGER.debug(root.find("header").find("vertical").text)

    # mdl.setVerticalHeaderLabels(vLabels)
    # mdl.setHorizontalHeaderLabels(hLabels)

    # Populates with empty items
    for i in enumerate(vLabels):
        row = []
        for r in enumerate(hLabels):
            row.append(QStandardItem())
        mdl.appendRow(row)

    # Data
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
                # mdl.setData(mdl.index(r, c, parent), col.text)
                item.setText(col.text)

            if "color" in col.attrib:
                # mdl.itemFromIndex(mdl.index(r, c, parent)).setIcon(iconFromColorString(col.attrib["color"]))
                item.setIcon(iconFromColorString(col.attrib["color"]))

            if len(col) != 0:
                # loadItem(col, mdl, mdl.index(r, c, parent))
                loadItem(col, mdl, mdl.indexFromItem(item))


def loadStandardItemModelXMLForCharacters(mdl, xml):
    """
    Loads a standardItemModel saved to XML by version 0, but for the new characterModel.
    @param mdl: characterModel
    @param xml: the content of the xml
    @return: nothing
    """
    mdl = mainWindow().mdlCharacter
    root = ET.fromstring(xml)
    data = root.find("data")

    for row in data:
        char = Character(mdl)

        for col in row:
            c = int(col.attrib["col"])

            # Value
            if col.text:
                char._data[c] = col.text

            # Color
            if "color" in col.attrib:
                char.setColor(QColor(col.attrib["color"]))

            # Infos
            if len(col) != 0:
                for rrow in col:
                    info = CharacterInfo(char)
                    for ccol in rrow:
                        cc = int(ccol.attrib["col"])
                        if cc == 11 and ccol.text:
                            info.description = ccol.text
                        if cc == 12 and ccol.text:
                            info.value = ccol.text
                    char.infos.append(info)

        mdl.characters.append(char)
