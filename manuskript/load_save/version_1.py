#!/usr/bin/env python
# --!-- coding: utf8 --!--

# Version 1 of file saving format.
# Aims at providing a plain-text way of saving a project
# (except for some elements), allowing collaborative work
# versioning and third-partty editing.
import os
import string
import zipfile

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QColor

from manuskript import settings
from manuskript.enums import Character, World, Plot, PlotStep, Outline
from manuskript.functions import mainWindow, iconColor
from lxml import etree as ET


try:
    import zlib  # Used with zipfile for compression

    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

cache = {}


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


def saveProject(zip=None):
    """
    Saves the project. If zip is False, the project is saved as a multitude of plain-text files for the most parts
    and some XML or zip? for settings and stuff.
    If zip is True, everything is saved as a single zipped file. Easier to carry around, but does not allow
    collaborative work, versionning, or third-party editing.
    @param zip: if True, saves as a single file. If False, saves as plain-text. If None, tries to determine based on
    settings.
    @return: Nothing
    """
    if zip is None:
        zip = False
        # Fixme

    # List of files to be written
    files = []
    # List of files to be removed
    removes = []

    mw = mainWindow()

    if zip:
        # File format version
        files.append(("VERSION", "1"))

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
        val = mw.mdlFlatData.item(0, col).text().strip()
        if val:
            content += "{name}:{spaces}{value}\n".format(
                name=name,
                spaces=" " * (15 - len(name)),
                value=val
            )
    files.append((path, content))

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
        val = mw.mdlFlatData.item(1, col).text().strip()
        if val:
            content += formatMetaData(name, val, 12)

    files.append((path, content))

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
                    color= "" if color == "" else ":" + " " * (20 - len(text)) + color
                )

        files.append((path, content))

    # Characters (self.mdlCharacter)
    # In a character folder

    path = os.path.join("characters", "{name}.txt")
    _map = [
        (Character.name, "Name"),
        (Character.ID,   "ID"),
        (Character.importance, "Importance"),
        (Character.motivation, "Motivation"),
        (Character.goal, "Goal"),
        (Character.conflict, "Conflict"),
        (Character.summarySentence, "Phrase Summary"),
        (Character.summaryPara, "Paragraph Summary"),
        (Character.summaryFull, "Full Summary"),
        (Character.notes, "Notes"),
    ]
    mdl = mw.mdlCharacter
    for c in mdl.characters:
        content = ""
        for m, name in _map:
            val = mdl.data(c.index(m.value)).strip()
            if val:
                content += formatMetaData(name, val, 20)

        for info in c.infos:
            content += formatMetaData(info.description, info.value, 20)

        cpath = path.format(name="{ID}-{slugName}".format(
            ID=c.ID(),
            slugName=slugify(c.name())
        ))
        # Has the character been renamed?
        # If so, we remove the old file (if not zipped)
        if c.lastPath and cpath != c.lastPath:
            removes.append(c.lastPath)
        c.lastPath = cpath
        files.append((
            cpath,
            content))

    # Texts
    # In an outline folder

    mdl = mw.mdlOutline
    for filename, content in exportOutlineItem(mdl.rootItem):
        files.append((filename, content))

    # World (mw.mdlWorld)
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

    # Plots (mw.mdlPlots)
    # Either in XML or lots of plain texts?
    # More probably XML since there is not really a lot if writing to do (third-party)

    path = "plots.xml"
    mdl = mw.mdlPlots

    root = ET.Element("root")
    addPlotItem(root, mdl)
    content = ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    files.append((path, content))

    # Settings
    # Saved in readable text (json) for easier versionning. But they mustn't be shared, it seems.
    # Maybe include them only if zipped?
    # Well, for now, we keep them here...
    files.append(("settings.txt", settings.save(protocol=0)))

    project = mw.currentProject

    # Save to zip
    if zip:
        project = os.path.join(
            os.path.dirname(project),
            "_" + os.path.basename(project)
        )

        zf = zipfile.ZipFile(project, mode="w")

        for filename, content in files:
            zf.writestr(filename, content, compress_type=compression)

        zf.close()

    # Save to plain text
    else:
        dir = os.path.dirname(project)
        folder = os.path.splitext(os.path.basename(project))[0]
        print("Saving to folder", folder)

        for path in removes:
            if path not in [p for p,c in files]:
                filename = os.path.join(dir, folder, path)
                print("* Removing", filename)
                os.remove(filename)
                cache.pop(path)

        for path, content in files:
            filename = os.path.join(dir, folder, path)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            print("* Saving file", filename)

            # TODO: the first time it saves, it will overwrite everything, since it's not yet in cache.
            #       Or we have to cache while loading.

            if not path in cache or cache[path] != content:
                print("  Not in cache or changed: we write")
                mode = "w"+ ("b" if type(content) == bytes else "")
                with open(filename, mode) as f:
                    f.write(content)
                cache[path] = content

            else:
                print("  In cache, and identical. Do nothing.")


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

            if not val:
                continue

            for w in Plot:
                if y == w.value:
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
                else:
                    outline.attrib.pop(Plot.characters.name)

            # List resolution steps as sub items
            elif y == Plot.steps.value:
                if mdl.hasChildren(index):
                    for cX in range(mdl.rowCount(index)):
                        step = ET.SubElement(outline, "step")
                        for cY in range(mdl.columnCount(index)):
                            cIndex = mdl.index(cX, cY, index)
                            val = mdl.data(cIndex)

                            for w in PlotStep:
                                if cY == w.value:
                                    step.attrib[w.name] = val

                outline.attrib.pop(Plot.steps.name)

    return root


def exportOutlineItem(root):
    """
    Takes an outline item, and returns an array of (`filename`, `content`) sets, representing the whole tree
    of items converted to mmd.

    @param root: OutlineItem
    @return: (str, str)
    """
    r = []
    path = "outline"

    k=0
    for child in root.children():
        spath = os.path.join(path, *outlineItemPath(child))
        k += 1

        if child.type() == "folder":
            fpath = os.path.join(spath, "folder.txt")
            content = outlineToMMD(child)
            r.append((fpath, content))

        elif child.type() in ["txt", "t2t"]:
            content = outlineToMMD(child)
            r.append((spath, content))

        elif child.type() in ["html"]:
            # Convert first
            pass

        else:
            print("Unknown type")

        r += exportOutlineItem(child)

    return r

def outlineItemPath(item):
    # Root item
    if not item.parent():
        return []
    else:
        name = "{ID}-{name}{ext}".format(
            ID=item.row(),
            name=slugify(item.title()),
            ext="" if item.type() == "folder" else ".{}".format(item.type())
        )
        return outlineItemPath(item.parent()) + [name]

def outlineToMMD(item):
    content = ""

    # We don't want to write some datas (computed)
    exclude = [Outline.wordCount, Outline.goal, Outline.goalPercentage, Outline.revisions, Outline.text]
    # We want to force some data even if they're empty
    force = [Outline.compile]

    for attrib in Outline:
        if attrib in exclude: continue
        val = item.data(attrib.value)
        if val or attrib in force:
            content += formatMetaData(attrib.name, str(val), 15)

    content += "\n\n"
    content += item.data(Outline.text.value)

    # Saving revisions
    # TODO
    # rev = item.revisions()
    # for r in rev:
    #     revItem = ET.Element("revision")
    #     revItem.set("timestamp", str(r[0]))
    #     revItem.set("text", r[1])
    #     item.append(revItem)

    return content

def loadProject(project):
    """
    Loads a project.
    @param project: the filename of the project to open.
    @return: an array of errors, empty if None.
    """

    # Don't forget to cache everything that is loaded
    # In order to save only what has changed.

    pass