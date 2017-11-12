#!/usr/bin/env python
# --!-- coding: utf8 --!--

from PyQt5.QtWidgets import qApp, QMessageBox
from manuskript.models.outlineModel import outlineItem
from manuskript.enums import Outline
from lxml import etree as ET
from manuskript.functions import mainWindow
from manuskript.importer.abstractImporter import abstractImporter

class mindMapImporter(abstractImporter):

    name = "Mind Map"
    description = ""
    fileFormat = "Mind map Files (*.mm)"
    icon = "text-x-opml+xml"

    @classmethod
    def isValid(cls):
        return True

    def startImport(self, filePath, parentItem, settingsWidget, fromString=None):
        """
        Import/export outline cards in mind map free plane.
        """
        ret = False

        if filePath != "":
            # We have a filePath, so we read the file
            try:
                with open(filePath, 'rb') as f:
                    content = f.read()
            except:
                return None

        elif fromString == "":
            # We have neither filePath nor fromString, so we leave
            return None

        else:
            # We load from string
            content = bytes(fromString, "utf-8")

        root = ET.fromstring(content)

        node = root.find("node")
        items = []

        if node is not None:
            items.extend(self.parseItems(node, parentItem))
            ret = True

        if not ret:
            QMessageBox.critical(
                settingsWidget,
                qApp.translate("Import", "Mind Map Import"),
                qApp.translate("Import", "This does not appear to be a valid Mind Map file."))

            return None

        return items

    def settingsWidget(self, widget):
        """
        Takes a QWidget that can be modified and must be returned.
        """

        # Add group
        group = self.addGroup(widget.toolBox.widget(0),
                              qApp.translate("Import", "Mind Map import"))

        self.addSetting("importTipAs", "combo",
                        qApp.translate("Import", "Import tip as:"),
                        vals="Folder|Text",
                       )

        for s in self.settings:
            self.settings[s].widget(group)

        return widget

    def parseItems(self, underElement, parentItem=None):
        items = []
        title = underElement.get('TEXT')
        if title is not None:

            item = outlineItem(parent=parentItem, title=title)
            items.append(item)

            children = underElement.findall('node')
            if children is not None and len(children) > 0:
                for c in children:
                    items.extend(self.parseItems(c, item))
            elif self.getSetting("importTipAs").value() == "Text":
                item.setData(Outline.type.value, 'md')

        return items
