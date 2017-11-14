#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os
from manuskript.importer.abstractImporter import abstractImporter
from manuskript.models.outlineModel import outlineItem
from manuskript.enums import Outline
from PyQt5.QtWidgets import qApp


class folderImporter(abstractImporter):

    name = "Folder"
    description = ""
    fileFormat = "<<folder>>"
    icon = "folder"

    @classmethod
    def isValid(cls):
        return True

    def startImport(self, filePath, parentItem, settingsWidget, fromString=None):
        """
        Imports from a folder.
        """
        ext = self.getSetting("ext").value()
        ext = [e.strip().replace("*", "").lower() for e in ext.split(",")]

        sorting = self.getSetting("sortItems").value()

        items = []
        stack = {}

        for dirpath, dirnames, filenames in os.walk(filePath):

            if dirpath in stack:
                item = stack[dirpath]
            else:
                # It's the parent folder, and we are not including it
                # so every item is attached to parentItem
                item = parentItem

            def addFile(f):
                fName, fExt = os.path.splitext(f)
                if fExt.lower() in ext:
                    try:
                        with open(os.path.join(dirpath, f), "r") as fr:
                            content = fr.read()
                        child = outlineItem(title=fName, _type="md", parent=item)
                        child._data[Outline.text] = content
                        items.append(child)
                    except UnicodeDecodeError:
                        # Probably not a text file
                        pass

            def addFolder(d):
                child = outlineItem(title=d, parent=item)
                items.append(child)
                stack[os.path.join(dirpath, d)] = child

            if not self.getSetting("separateFolderFiles").value():
                # Import folder and files together (only makes differences if
                # they are sorted, really)
                allFiles = dirnames + filenames
                if sorting:
                    allFiles = sorted(allFiles)

                for f in allFiles:
                    if f in dirnames:
                        addFolder(f)
                    else:
                        addFile(f)

            else:
                # Import first folders, then files
                if sorting:
                    dirnames = sorted(dirnames)
                    filenames = sorted(filenames)

                # Import folders
                for d in dirnames:
                    addFolder(d)

                # Import files
                for f in filenames:
                    addFile(f)

        return items

    def settingsWidget(self, widget):
        """
        Takes a QWidget that can be modified and must be returned.
        """

        # Add group
        group = self.addGroup(widget.toolBox.widget(0),
                              qApp.translate("Import", "Folder import"))
        #group = cls.addPage(widget, "Folder import")

        self.addSetting("info", "label",
                        qApp.translate("Import", """<p><b>Info:</b> Imports a whole
                        directory structure. Folders are added as folders, and
                        plaintext documents within (you chose which ones by extension)
                        are added as scene.</p>
                        <p>Only text files are supported (not images, binary or others).</p>"""))

        self.addSetting("ext", "text",
                        qApp.translate("Import", "Include only those extensions:"),
                        default="*.txt, *.md",
                        tooltip=qApp.translate("Import", "Coma separated values")),

        self.addSetting("sortItems", "checkbox",
                        qApp.translate("Import", "Sort items by name"),
                        default=True),

        self.addSetting("separateFolderFiles", "checkbox",
                        qApp.translate("Import", "Import folder then files"),
                        default=True),

        self.addSettingsTo(group)

        return widget




