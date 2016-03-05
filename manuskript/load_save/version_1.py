#!/usr/bin/env python
# --!-- coding: utf8 --!--

# Version 1 of file saving format.
# Aims at providing a plain-text way of saving a project
# (except for some elements), allowing collaborative work
# versioning and third-partty editing.
import os
import zipfile

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from manuskript import settings
from manuskript.enums import Character
from manuskript.functions import mainWindow, iconColor

try:
    import zlib  # Used with zipfile for compression

    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED


cache = {}


def formatMetaData(name, value, tabLength=10):

    # TODO: escape ":" in name
    return "{name}:{spaces}{value}\n".format(
        name=name,
        spaces=" " * (tabLength - len(name)),
        value=value
    )


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


    files = []
    mw = mainWindow()

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
        val = "\n".join([" " * 13 + l for l in val.split("\n")])[13:]
        if val:
            content += "{name}:{spaces}{value}\n".format(
                name=name,
                spaces=" " * (12 - len(name)),
                value=val
            )
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

    path = os.path.join("characters", "{name}.txt")  # Not sure wheter os.path allows this
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
        LENGTH = 20
        for m, name in _map:
            val = mdl.data(c.index(m.value)).strip()
            if val:
                # Multiline formatting
                if len(val.split("\n")) > 1:
                    val = "\n".join([" " * (LENGTH + 1) + l for l in val.split("\n")])[LENGTH + 1:]

                content += formatMetaData(name, val, LENGTH)

        for info in c.infos:
            content += formatMetaData(info.description, info.value, LENGTH)

        name = "{ID}-{slugName}".format(
            ID=c.ID(),
            slugName="FIXME"
        )
        files.append((
            path.format(name=name),
            content))

    # Texts
    # In an outline folder

    # TODO

    # World (mw.mdlWorld)
    # Either in an XML file, or in lots of plain texts?
    # More probably text, since there might be writing done in third-party.

    # TODO

    # Plots (mw.mdlPlots)
    # Either in XML or lots of plain texts?
    # More probably XML since there is not really a lot if writing to do (third-party)

    # TODO

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


def loadProject(project):
    """
    Loads a project.
    @param project: the filename of the project to open.
    @return: an array of errors, empty if None.
    """

    # Don't forget to cache everything that is loaded
    # In order to save only what has changed.

    pass