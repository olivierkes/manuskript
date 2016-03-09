#!/usr/bin/env python
# --!-- coding: utf8 --!--

# Version 1 of file saving format.
# Aims at providing a plain-text way of saving a project
# (except for some elements), allowing collaborative work
# versioning and third-partty editing.
import os, shutil
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


def log(*args):
    print(" ".join(str(a) for a in args))


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

    log("\n\nSaving to:", "zip" if zip else "folder")

    # List of files to be written
    files = []
    # List of files to be removed
    removes = []
    # List of files to be moved
    moves = []

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
        val = mw.mdlFlatData.item(1, col).text().strip()
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
                    color= "" if color == "" else ":" + " " * (20 - len(text)) + color
                )

        files.append((path, content))

    ####################################################################################################################
    # Characters
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

    # Review characters
    for c in mdl.characters:

        # Generates file's content
        content = ""
        for m, name in _map:
            val = mdl.data(c.index(m.value)).strip()
            if val:
                content += formatMetaData(name, val, 20)

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

    # # List removed characters
    # for c in mdl.removed:
    #     # generate file's path
    #     cpath = path.format(name="{ID}-{slugName}".format(
    #         ID=c.ID(),
    #         slugName=slugify(c.name())
    #     ))
    #
    #     # Mark for removal
    #     removes.append(cpath)

    mdl.removed.clear()

    ####################################################################################################################
    # Texts
    # In an outline folder

    mdl = mw.mdlOutline

    # Go through the tree
    f, m, r = exportOutlineItem(mdl.rootItem)
    files += f
    moves += m
    removes += r

    # List removed items
    # for item in mdl.removed:
    #     path = outlineItemPath(item)
    #     log("* Marking for removal:", path)


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

    ####################################################################################################################
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

            # TODO: the first time it saves, it will overwrite everything, since it's not yet in cache.
            #       Or we have to cache while loading.

            if not path in cache or cache[path] != content:
                log("* Writing file", path)
                mode = "w"+ ("b" if type(content) == bytes else "")
                with open(filename, mode) as f:
                    f.write(content)
                cache[path] = content

            else:
                pass
                # log("  In cache, and identical. Do nothing.")

        # Removing phantoms
        for path in [p for p in cache if p not in [p for p,c in files]]:
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
    Takes an outline item, and returns two lists:
    1. of (`filename`, `content`), representing the whole tree of files to be written, in multimarkdown.
    3. of (`filename`, `filename`) listing files to be moved
    2. of `filename`, representing files to be removed.

    @param root: OutlineItem
    @return: [(str, str)], [str]
    """

    files = []
    moves = []
    removes = []

    k=0
    for child in root.children():
        itemPath = outlineItemPath(child)
        spath = os.path.join(*itemPath)

        k += 1

        # Has the item been renamed?
        lp = child._lastPath
        if lp and spath != lp:
            moves.append((lp, spath))
            log(child.title(), "has been renamed (", lp, " → ", spath, ")")
            log(" → We mark for moving:", lp)

        # Updates item last's path
        child._lastPath = spath # itemPath[-1]

        # Generating content
        if child.type() == "folder":
            fpath = os.path.join(spath, "folder.txt")
            content = outlineToMMD(child)
            files.append((fpath, content))

        elif child.type() in ["txt", "t2t"]:
            content = outlineToMMD(child)
            files.append((spath, content))

        elif child.type() in ["html"]:
            # Save as html. Not the most beautiful, but hey.
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
        name = "{ID}-{name}{ext}".format(
            ID=item.row(),
            name=slugify(item.title()),
            ext="" if item.type() == "folder" else ".md"  # ".{}".format(item.type())  # To have .txt, .t2t, .html, ...
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
    # TODO: saving revisions?
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