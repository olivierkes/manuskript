#!/usr/bin/env python
# --!-- coding: utf8 --!--

# Version 1 of file saving format.
# Aims at providing a plain-text way of saving a project
# (except for some elements), allowing collaborative work
# versioning and third-partty editing.

import os
import re
import shutil
import string
import zipfile
from collections import OrderedDict

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QColor, QStandardItem

from manuskript import settings
from manuskript.enums import Character, World, Plot, PlotStep, Outline
from manuskript.functions import mainWindow, iconColor, iconFromColorString
from manuskript.converters import HTML2PlainText
from lxml import etree as ET

from manuskript.load_save.version_0 import loadFilesFromZip
from manuskript.models.characterModel import CharacterInfo
from manuskript.models.outlineModel import outlineItem

try:
    import zlib  # Used with zipfile for compression

    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

cache = {}


characterMap = OrderedDict([
    (Character.name, "Name"),
    (Character.ID,   "ID"),
    (Character.importance, "Importance"),
    (Character.motivation, "Motivation"),
    (Character.goal, "Goal"),
    (Character.conflict, "Conflict"),
    (Character.epiphany, "Epiphany"),
    (Character.summarySentence, "Phrase Summary"),
    (Character.summaryPara, "Paragraph Summary"),
    (Character.summaryFull, "Full Summary"),
    (Character.notes, "Notes"),
])

# If true, logs infos while saving and loading.
LOG = False

def formatMetaData(name, value, tabLength=10):

    # Multiline formatting
    if len(value.split("\n")) > 1:
        value = "\n".join([" " * (tabLength + 1) + l for l in value.split("\n")])[tabLength + 1:]

    # Avoid empty description (don't know how much MMD loves that)
    if name == "":
        name = "None"

    # Escapes ":" in name
    name = name.replace(":", "_.._")

    return "{name}:{spaces}{value}\n".format(
        name=name,
        spaces=" " * (tabLength - len(name)),
        value=value
    )


def slugify(name):
    """
    A basic slug function, that escapes all spaces to "_" and all non letters/digits to "-".
    @param name: name to slugify (str)
    @return: str
    """
    valid = string.ascii_letters + string.digits
    newName = ""
    for c in name:
        if c in valid:
            newName += c
        elif c in string.whitespace:
            newName += "_"
        else:
            newName += "-"
    return newName


def log(*args):
    if LOG:
        print(" ".join(str(a) for a in args))


def saveProject(zip=None):
    """
    Saves the project. If zip is False, the project is saved as a multitude of plain-text files for the most parts
    and some XML or zip? for settings and stuff.
    If zip is True, everything is saved as a single zipped file. Easier to carry around, but does not allow
    collaborative work, versionning, or third-party editing.
    @param zip: if True, saves as a single file. If False, saves as plain-text. If None, tries to determine based on
    settings.
    @return: True if successful, False otherwise.
    """
    if zip is None:
        zip = settings.saveToZip

    log("\n\nSaving to:", "zip" if zip else "folder")

    # List of files to be written
    files = []
    # List of files to be removed
    removes = []
    # List of files to be moved
    moves = []

    mw = mainWindow()

    # File format version
    files.append(("MANUSKRIPT", "1"))

    # General infos (book and author)
    # Saved in plain text, in infos.txt

    path = "infos.txt"
    content = ""
    for name, col in [
            ("Title", 0),
            ("Subtitle", 1),
            ("Serie", 2),
            ("Volume", 3),
            ("Genre", 4),
            ("License", 5),
            ("Author", 6),
            ("Email", 7),
            ]:
        item = mw.mdlFlatData.item(0, col)
        if item:
            val = item.text().strip()
        else:
            val = ""

        if val:
            content += "{name}:{spaces}{value}\n".format(
                name=name,
                spaces=" " * (15 - len(name)),
                value=val
            )
    files.append((path, content))

    ####################################################################################################################
    # Summary
    # In plain text, in summary.txt

    path = "summary.txt"
    content = ""
    for name, col in [
            ("Situation", 0),
            ("Sentence", 1),
            ("Paragraph", 2),
            ("Page", 3),
            ("Full", 4),
            ]:
        item = mw.mdlFlatData.item(1, col)
        if item:
            val = item.text().strip()
        else:
            val = ""

        if val:
            content += formatMetaData(name, val, 12)

    files.append((path, content))

    ####################################################################################################################
    # Label & Status
    # In plain text

    for mdl, path in [
        (mw.mdlStatus, "status.txt"),
        (mw.mdlLabels, "labels.txt")
    ]:

        content = ""

        # We skip the first row, which is empty and transparent
        for i in range(1, mdl.rowCount()):
            color = ""
            if mdl.data(mdl.index(i, 0), Qt.DecorationRole) is not None:
                color = iconColor(mdl.data(mdl.index(i, 0), Qt.DecorationRole)).name(QColor.HexRgb)
                color = color if color != "#ff000000" else "#00000000"

            text = mdl.data(mdl.index(i, 0))

            if text:
                content += "{name}{color}\n".format(
                    name=text,
                    color="" if color == "" else ":" + " " * (20 - len(text)) + color
                )

        files.append((path, content))

    ####################################################################################################################
    # Characters
    # In a character folder

    path = os.path.join("characters", "{name}.txt")
    mdl = mw.mdlCharacter

    # Review characters
    for c in mdl.characters:

        # Generates file's content
        content = ""
        for m in characterMap:
            val = mdl.data(c.index(m.value)).strip()
            if val:
                content += formatMetaData(characterMap[m], val, 20)

        # Character's color:
        content += formatMetaData("Color", c.color().name(QColor.HexRgb), 20)

        # Character's infos
        for info in c.infos:
            content += formatMetaData(info.description, info.value, 20)

        # generate file's path
        cpath = path.format(name="{ID}-{slugName}".format(
            ID=c.ID(),
            slugName=slugify(c.name())
        ))

        # Has the character been renamed?
        if c.lastPath and cpath != c.lastPath:
            moves.append((c.lastPath, cpath))

        # Update character's path
        c.lastPath = cpath

        files.append((cpath, content))

    ####################################################################################################################
    # Texts
    # In an outline folder

    mdl = mw.mdlOutline

    # Go through the tree
    f, m, r = exportOutlineItem(mdl.rootItem)
    files += f
    moves += m
    removes += r

    # Writes revisions (if asked for)
    if settings.revisions["keep"]:
        files.append(("revisions.xml", mdl.saveToXML()))

    ####################################################################################################################
    # World
    # Either in an XML file, or in lots of plain texts?
    # More probably text, since there might be writing done in third-party.

    path = "world.opml"
    mdl = mw.mdlWorld

    root = ET.Element("opml")
    root.attrib["version"] = "1.0"
    body = ET.SubElement(root, "body")
    addWorldItem(body, mdl)
    content = ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    files.append((path, content))

    ####################################################################################################################
    # Plots (mw.mdlPlots)
    # Either in XML or lots of plain texts?
    # More probably XML since there is not really a lot if writing to do (third-party)

    path = "plots.xml"
    mdl = mw.mdlPlots

    root = ET.Element("root")
    addPlotItem(root, mdl)
    content = ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    files.append((path, content))

    ####################################################################################################################
    # Settings
    # Saved in readable text (json) for easier versionning. But they mustn't be shared, it seems.
    # Maybe include them only if zipped?
    # Well, for now, we keep them here...

    files.append(("settings.txt", settings.save(protocol=0)))

    project = mw.currentProject

    # We check if the file exist and we have write access. If the file does
    # not exists, we check the parent folder, because it might be a new project.
    if os.path.exists(project) and not os.access(project, os.W_OK) or \
       not os.path.exists(project) and not os.access(os.path.dirname(project), os.W_OK):
        print("Error: you don't have write access to save this project there.")
        return False

    ####################################################################################################################
    # Save to zip

    if zip:
        # project = os.path.join(
        #     os.path.dirname(project),
        #     "_" + os.path.basename(project)
        # )

        zf = zipfile.ZipFile(project, mode="w")

        for filename, content in files:
            zf.writestr(filename, content, compress_type=compression)

        zf.close()
        return True

    ####################################################################################################################
    # Save to plain text

    else:

        global cache

        # Project path
        dir = os.path.dirname(project)

        # Folder containing file: name of the project file (without .msk extension)
        folder = os.path.splitext(os.path.basename(project))[0]

        # Debug
        log("\nSaving to folder", folder)

        # If cache is empty (meaning we haven't loaded from disk), we wipe folder, just to be sure.
        if not cache:
            if os.path.exists(os.path.join(dir, folder)):
                shutil.rmtree(os.path.join(dir, folder))

        # Moving files that have been renamed
        for old, new in moves:

            # Get full path
            oldPath = os.path.join(dir, folder, old)
            newPath = os.path.join(dir, folder, new)

            # Move the old file to the new place
            try:
                os.replace(oldPath, newPath)
                log("* Renaming/moving {} to {}".format(old, new))
            except FileNotFoundError:
                # Maybe parent folder has been renamed
                pass

            # Update cache
            cache2 = {}
            for f in cache:
                f2 = f.replace(old, new)
                if f2 != f:
                    log("  * Updating cache:", f, f2)
                cache2[f2] = cache[f]
            cache = cache2

        # Writing files
        for path, content in files:
            filename = os.path.join(dir, folder, path)
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Check if content is in cache, and write if necessary
            if path not in cache or cache[path] != content:
                log("* Writing file {} ({})".format(path, "not in cache" if path not in cache else "different"))
                # mode = "w" + ("b" if type(content) == bytes else "")
                if type(content) == bytes:
                    with open(filename, "wb") as f:
                        f.write(content)
                else:
                    with open(filename, "w", encoding='utf8') as f:
                        f.write(content)

                cache[path] = content

        # Removing phantoms
        for path in [p for p in cache if p not in [p for p, c in files]]:
            filename = os.path.join(dir, folder, path)
            log("* Removing", path)

            if os.path.isdir(filename):
                shutil.rmtree(filename)

            else:  # elif os.path.exists(filename)
                os.remove(filename)

            # Clear cache
            cache.pop(path, 0)

        # Removing empty directories
        for root, dirs, files in os.walk(os.path.join(dir, folder, "outline")):
            for dir in dirs:
                newDir = os.path.join(root, dir)
                try:
                    os.removedirs(newDir)
                    log("* Removing empty directory:", newDir)
                except:
                    # Directory not empty, we don't remove.
                    pass

        # Write the project file's content
        with open(project, "w", encoding='utf8') as f:
            f.write("1")  # Format number

        return True


def addWorldItem(root, mdl, parent=QModelIndex()):
    """
    Lists elements in a world model and create an OPML xml file.
    @param root: an Etree element
    @param mdl:  a worldModel
    @param parent: the parent index in the world model
    @return: root, to which sub element have been added
    """
    # List every row (every world item)
    for x in range(mdl.rowCount(parent)):

        # For each row, create an outline item.
        outline = ET.SubElement(root, "outline")
        for y in range(mdl.columnCount(parent)):

            val = mdl.data(mdl.index(x, y, parent))

            if not val:
                continue

            for w in World:
                if y == w.value:
                    outline.attrib[w.name] = val

            if mdl.hasChildren(mdl.index(x, y, parent)):
                addWorldItem(outline, mdl, mdl.index(x, y, parent))

    return root


def addPlotItem(root, mdl, parent=QModelIndex()):
    """
    Lists elements in a plot model and create an xml file.
    @param root: an Etree element
    @param mdl:  a plotModel
    @param parent: the parent index in the plot model
    @return: root, to which sub element have been added
    """

    # List every row (every plot item)
    for x in range(mdl.rowCount(parent)):

        # For each row, create an outline item.
        outline = ET.SubElement(root, "plot")
        for y in range(mdl.columnCount(parent)):

            index = mdl.index(x, y, parent)
            val = mdl.data(index)
            #
            # if not val:
            #     continue

            for w in Plot:
                if y == w.value and val:
                    outline.attrib[w.name] = val

            # List characters as attrib
            if y == Plot.characters.value:
                if mdl.hasChildren(index):
                    characters = []
                    for cX in range(mdl.rowCount(index)):
                        for cY in range(mdl.columnCount(index)):
                            cIndex = mdl.index(cX, cY, index)
                            characters.append(mdl.data(cIndex))
                    outline.attrib[Plot.characters.name] = ",".join(characters)

                elif Plot.characters.name in outline.attrib:
                    outline.attrib.pop(Plot.characters.name)

            # List resolution steps as sub items
            elif y == Plot.steps.value:
                if mdl.hasChildren(index):
                    for cX in range(mdl.rowCount(index)):
                        step = ET.SubElement(outline, "step")
                        for cY in range(mdl.columnCount(index)):
                            cIndex = mdl.index(cX, cY, index)
                            # If empty, returns None, which creates trouble later with lxml, so default to ""
                            val = mdl.data(cIndex) or ""

                            for w in PlotStep:
                                if cY == w.value and w.name:
                                    step.attrib[w.name] = val

                elif Plot.steps.name in outline.attrib:
                    outline.attrib.pop(Plot.steps.name)

    return root


def exportOutlineItem(root):
    """
    Takes an outline item, and returns three lists:
    1. of (`filename`, `content`), representing the whole tree of files to be written, in multimarkdown.
    2. of (`filename`, `filename`) listing files to be moved
    3. of `filename`, representing files to be removed.

    @param root: OutlineItem
    @return: [(str, str)], [(str, str)], [str]
    """

    files = []
    moves = []
    removes = []

    k = 0
    for child in root.children():
        spath = os.path.join(*outlineItemPath(child))

        k += 1

        # Has the item been renamed?
        lp = child._lastPath
        if lp and spath != lp:
            moves.append((lp, spath))
            log(child.title(), "has been renamed (", lp, " → ", spath, ")")
            log(" → We mark for moving:", lp)

        # Updates item last's path
        child._lastPath = spath

        # Generating content
        if child.type() == "folder":
            fpath = os.path.join(spath, "folder.txt")
            content = outlineToMMD(child)
            files.append((fpath, content))

        elif child.type() == "md":
            content = outlineToMMD(child)
            files.append((spath, content))

        else:
            log("Unknown type")

        f, m, r = exportOutlineItem(child)
        files += f
        moves += m
        removes += r

    return files, moves, removes


def outlineItemPath(item):
    """
    Returns the outlineItem file path (like the path where it will be written on the disk). As a list of folder's
    name. To be joined by os.path.join.
    @param item: outlineItem
    @return: list of folder's names
    """
    # Root item
    if not item.parent():
        return ["outline"]
    else:
        # Count the number of siblings for padding '0'
        siblings = item.parent().childCount()

        # We check if multiple items have the same name
        # If so, we add "-ID" to their name
        siblingsNames = [s.title() for s in item.parent().children()]
        if siblingsNames.count(item.title()) > 1:
            title = "{}-{}".format(item.title(), item.ID())
        else:
            title = item.title()

        name = "{ID}-{name}{ext}".format(
            ID=str(item.row()).zfill(len(str(siblings))),
            name=slugify(title),
            ext="" if item.type() == "folder" else ".md"
        )
        return outlineItemPath(item.parent()) + [name]


def outlineToMMD(item):
    content = ""

    # We don't want to write some datas (computed)
    exclude = [Outline.wordCount, Outline.goal, Outline.goalPercentage, Outline.revisions, Outline.text]
    # We want to force some data even if they're empty
    force = [Outline.compile]

    for attrib in Outline:
        if attrib in exclude:
            continue
        val = item.data(attrib.value)
        if val or attrib in force:
            content += formatMetaData(attrib.name, str(val), 15)

    content += "\n\n"
    content += item.data(Outline.text.value)

    return content

########################################################################################################################
# LOAD
########################################################################################################################

def loadProject(project, zip=None):
    """
    Loads a project.
    @param project: the filename of the project to open.
    @param zip: whether the project is a zipped or not.
    @return: an array of errors, empty if None.
    """

    mw = mainWindow()
    errors = []

    ####################################################################################################################
    # Read and store everything in a dict

    log("\nLoading {} ({})".format(project, "ZIP" if zip else "not zip"))
    if zip:
        files = loadFilesFromZip(project)

        # Decode files
        for f in files:
            if f[-4:] not in [".xml", "opml"]:
                files[f] = files[f].decode("utf-8")

    else:
        # Project path
        dir = os.path.dirname(project)

        # Folder containing file: name of the project file (without .msk extension)
        folder = os.path.splitext(os.path.basename(project))[0]

        # The full path towards the folder containing files
        path = os.path.join(dir, folder, "")

        files = {}
        for dirpath, dirnames, filenames in os.walk(path):
            p = dirpath.replace(path, "")
            for f in filenames:
                # mode = "r" + ("b" if f[-4:] in [".xml", "opml"] else "")
                if f[-4:] in [".xml", "opml"]:
                    with open(os.path.join(dirpath, f), "rb") as fo:
                        files[os.path.join(p, f)] = fo.read()
                else:
                    with open(os.path.join(dirpath, f), "r", encoding="utf8") as fo:
                        files[os.path.join(p, f)] = fo.read()

        # Saves to cache (only if we loaded from disk and not zip)
        global cache
        cache = files

        # FIXME: watch directory for changes

    # Sort files by keys
    files = OrderedDict(sorted(files.items()))

    ####################################################################################################################
    # Settings

    if "settings.txt" in files:
        settings.load(files["settings.txt"], fromString=True, protocol=0)
    else:
        errors.append("settings.txt")

    # Just to be sure
    settings.saveToZip = zip
    settings.defaultTextType = "md"

    ####################################################################################################################
    # Labels

    mdl = mw.mdlLabels
    mdl.appendRow(QStandardItem(""))  # Empty = No labels
    if "labels.txt" in files:
        log("\nReading labels:")
        for s in files["labels.txt"].split("\n"):
            if not s:
                continue

            m = re.search(r"^(.*?):\s*(.*)$", s)
            txt = m.group(1)
            col = m.group(2)
            log("* Add status: {} ({})".format(txt, col))
            icon = iconFromColorString(col)
            mdl.appendRow(QStandardItem(icon, txt))

    else:
        errors.append("labels.txt")

    ####################################################################################################################
    # Status

    mdl = mw.mdlStatus
    mdl.appendRow(QStandardItem(""))  # Empty = No status
    if "status.txt" in files:
        log("\nReading Status:")
        for s in files["status.txt"].split("\n"):
            if not s:
                continue
            log("* Add status:", s)
            mdl.appendRow(QStandardItem(s))
    else:
        errors.append("status.txt")

    ####################################################################################################################
    # Infos

    mdl = mw.mdlFlatData
    if "infos.txt" in files:
        md, body = parseMMDFile(files["infos.txt"], asDict=True)

        row = []
        for name in ["Title", "Subtitle", "Serie", "Volume", "Genre", "License", "Author", "Email"]:
            row.append(QStandardItem(md.get(name, "")))

        mdl.appendRow(row)

    else:
        errors.append("infos.txt")

    ####################################################################################################################
    # Summary

    mdl = mw.mdlFlatData
    if "summary.txt" in files:
        md, body = parseMMDFile(files["summary.txt"], asDict=True)

        row = []
        for name in ["Situation", "Sentence", "Paragraph", "Page", "Full"]:
            row.append(QStandardItem(md.get(name, "")))

        mdl.appendRow(row)

    else:
        errors.append("summary.txt")

    ####################################################################################################################
    # Plots

    mdl = mw.mdlPlots
    if "plots.xml" in files:
        log("\nReading plots:")
        # xml = bytearray(files["plots.xml"], "utf-8")
        root = ET.fromstring(files["plots.xml"])

        for plot in root:
            # Create row
            row = getStandardItemRowFromXMLEnum(plot, Plot)

            # Log
            log("* Add plot: ", row[0].text())

            # Characters
            if row[Plot.characters.value].text():
                IDs = row[Plot.characters.value].text().split(",")
                item = QStandardItem()
                for ID in IDs:
                    item.appendRow(QStandardItem(ID.strip()))
                row[Plot.characters.value] = item

            # Subplots
            for step in plot:
                row[Plot.steps.value].appendRow(
                    getStandardItemRowFromXMLEnum(step, PlotStep)
                )

            # Add row to the model
            mdl.appendRow(row)

    else:
        errors.append("plots.xml")

    ####################################################################################################################
    # World

    mdl = mw.mdlWorld
    if "world.opml" in files:
        log("\nReading World:")
        # xml = bytearray(files["plots.xml"], "utf-8")
        root = ET.fromstring(files["world.opml"])
        body = root.find("body")

        for outline in body:
            row = getOutlineItem(outline, World)
            mdl.appendRow(row)

    else:
        errors.append("world.opml")

    ####################################################################################################################
    # Characters

    mdl = mw.mdlCharacter
    log("\nReading Characters:")
    for f in [f for f in files if "characters" in f]:
        md, body = parseMMDFile(files[f])
        c = mdl.addCharacter()
        c.lastPath = f

        color = False
        for desc, val in md:

            # Base infos
            if desc in characterMap.values():
                key = [key for key, value in characterMap.items() if value == desc][0]
                index = c.index(key.value)
                mdl.setData(index, val)

            # Character color
            elif desc == "Color" and not color:
                c.setColor(QColor(val))
                # We remember the first time we found "Color": it is the icon color.
                # If "Color" comes a second time, it is a Character's info.
                color = True

            # Character's infos
            else:
                c.infos.append(CharacterInfo(c, desc, val))

        log("* Adds {} ({})".format(c.name(), c.ID()))

    ####################################################################################################################
    # Texts
    # We read outline form the outline folder. If revisions are saved, then there's also a revisions.xml which contains
    # everything, but the outline folder takes precedence (in cases it's been edited outside of manuksript.

    mdl = mw.mdlOutline
    log("\nReading outline:")
    paths = [f for f in files if "outline" in f]
    outline = OrderedDict()

    # We create a structure of imbricated OrderedDict to store the whole tree.
    for f in paths:
        split = f.split(os.path.sep)[1:]
        # log("* ", split)

        last = ""
        parent = outline
        parentLastPath = "outline"
        for i in split:
            if last:
                parent = parent[last]
                parentLastPath = os.path.join(parentLastPath, last)
            last = i

            if not i in parent:
                # If not last item, then it is a folder
                if i != split[-1]:
                    parent[i] = OrderedDict()

                # If file, we store it
                else:
                    parent[i] = files[f]

                # We store f to add it later as lastPath
                parent[i + ":lastPath"] = os.path.join(parentLastPath, i)



    # We now just have to recursively add items.
    addTextItems(mdl, outline)

    # Adds revisions
    if "revisions.xml" in files:
        root = ET.fromstring(files["revisions.xml"])
        appendRevisions(mdl, root)

    # Check IDS
    mdl.rootItem.checkIDs()

    return errors


def addTextItems(mdl, odict, parent=None):
    """
    Adds a text / outline items from an OrderedDict.
    @param mdl: model to add to
    @param odict: OrderedDict
    @return: nothing
    """
    if parent is None:
        parent = mdl.rootItem

    for k in odict:

        # In case k is a folder:
        if type(odict[k]) == OrderedDict and "folder.txt" in odict[k]:

            # Adds folder
            log("{}* Adds {} to {} (folder)".format("  " * parent.level(), k, parent.title()))
            item = outlineFromMMD(odict[k]["folder.txt"], parent=parent)
            item._lastPath = odict[k + ":lastPath"]

            # Read content
            addTextItems(mdl, odict[k], parent=item)

        # k is not a folder
        elif type(odict[k]) == str and k != "folder.txt" and not ":lastPath" in k:
            log("{}* Adds {} to {} (file)".format("  " * parent.level(), k, parent.title()))
            item = outlineFromMMD(odict[k], parent=parent)
            item._lastPath = odict[k + ":lastPath"]

        elif not ":lastPath" in k and k != "folder.txt":
            print("* Strange things in file {}".format(k))


def outlineFromMMD(text, parent):
    """
    Creates outlineItem from multimarkdown file.
    @param text: content of the file
    @param parent: appends item to parent (outlineItem)
    @return: outlineItem
    """

    item = outlineItem(parent=parent)
    md, body = parseMMDFile(text, asDict=True)

    # Store metadata
    for k in md:
        if k in Outline.__members__:
            item.setData(Outline.__members__[k].value, str(md[k]))

    # Store body
    item.setData(Outline.text.value, str(body))

    # Set file format to "md"
    # (Old version of manuskript had different file formats: text, t2t, html and md)
    # If file format is html, convert to plain text:
    if item.type() == "html":
        item.setData(Outline.text.value, HTML2PlainText(body))
    if item.type() in ["txt", "t2t", "html"]:
        item.setData(Outline.type.value, "md")

    return item


def appendRevisions(mdl, root):
    """
    Parse etree item to find outlineItem's with revisions, and adds them to model `mdl`.
    @param mdl: outlineModel
    @param root: etree
    @return: nothing
    """
    for child in root:
        # Recursively go through items
        if child.tag == "outlineItem":
            appendRevisions(mdl, child)

        # Revision found.
        elif child.tag == "revision":
            # Get root's ID
            ID = root.attrib["ID"]
            if not ID:
                log("* Serious problem: no ID!")
                continue

            # Find outline item in model
            item = mdl.getItemByID(ID)
            if not item:
                log("* Error: no item whose ID is", ID)
                continue

            # Store revision
            log("* Appends revision ({}) to {}".format(child.attrib["timestamp"], item.title()))
            item.appendRevision(child.attrib["timestamp"], child.attrib["text"])


def getOutlineItem(item, enum):
    """
    Reads outline items from an opml file. Returns a row of QStandardItem, easy to add to a QStandardItemModel.
    @param item: etree item
    @param enum: enum to read keys from
    @return: [QStandardItem]
    """
    row = getStandardItemRowFromXMLEnum(item, enum)
    log("* Add worldItem:", row[0].text())
    for child in item:
        sub = getOutlineItem(child, enum)
        row[0].appendRow(sub)

    return row


def getStandardItemRowFromXMLEnum(item, enum):
    """
    Reads and etree item and creates a row of QStandardItems by cross-referencing an enum.
    Returns a list of QStandardItems that can be added to a QStandardItemModel by appendRow.
    @param item: the etree item
    @param enum: the enum
    @return: list of QStandardItems
    """
    row = []
    for i in range(len(enum)):
        row.append(QStandardItem(""))

    for name in item.attrib:
        if name in enum.__members__:
            row[enum[name].value] = QStandardItem(item.attrib[name])
    return row

def parseMMDFile(text, asDict=False):
    """
    Takes the content of a MultiMarkDown file (str) and returns:
    1. A list containing metadatas: (description, value) if asDict is False.
       If asDict is True, returns metadatas as an OrderedDict. Be aware that if multiple metadatas have the same description
       (which is stupid, but hey), they will be lost except the last one.
    2. The body of the file
    @param text: the content of the file
    @return: (list, str) or (OrderedDict, str)
    """
    md = []
    mdd = OrderedDict()
    body = []
    descr = ""
    val = ""
    inBody = False
    for s in text.split("\n"):
        if not inBody:
            m = re.match(r"^([^\s].*?):\s*(.*)$", s)
            if m:
                # Commit last metadata
                if descr:
                    if descr == "None":
                        descr = ""
                    md.append((descr, val))
                    mdd[descr] = val
                descr = ""
                val = ""

                # Store new values
                descr = m.group(1)
                val = m.group(2)

            elif s[:4] == "    ":
                val += "\n" + s.strip()

            elif s == "":
                # End of metadatas
                inBody = True

                # Commit last metadata
                if descr:
                    if descr == "None":
                        descr = ""
                    md.append((descr, val))
                    mdd[descr] = val

        else:
            body.append(s)

    # We remove the second empty line (since we save with two empty lines)
    if body and body[0] == "":
        body = body[1:]

    body = "\n".join(body)

    if not asDict:
        return md, body
    else:
        return mdd, body


