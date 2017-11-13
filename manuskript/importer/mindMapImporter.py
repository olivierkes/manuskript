#!/usr/bin/env python
# --!-- coding: utf8 --!--

from PyQt5.QtWidgets import qApp, QMessageBox
from manuskript.models.outlineModel import outlineItem
from manuskript.enums import Outline
from lxml import etree as ET
from manuskript.functions import mainWindow
from manuskript.importer.abstractImporter import abstractImporter
from manuskript.converters import HTML2MD, HTML2PlainText

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
                        vals="Text|Folder",
                       )

        for s in self.settings:
            self.settings[s].widget(group)

        return widget

    def parseItems(self, underElement, parentItem=None):
        items = []

        # Title
        title = underElement.get('TEXT', "").replace("\n", " ")
        if not title:
            title = qApp.translate("Import", "Untitled")

        item = outlineItem(parent=parentItem, title=title)
        items.append(item)

        # URL
        url = underElement.get('LINK', None)

        # Rich text content
        content = ""
        content = underElement.find("richcontent")
        if content is not None:
            # In Freemind, can be note or node
            # Note: it's a note
            # Node: it's the title of the node, in rich text
            content_type = content.get("TYPE", "NOTE")
            content = ET.tostring(content.find("html"))

        if content and content_type == "NODE":
            # Content is title
            # convert rich text title (in html) to plain text
            title = HTML2PlainText(content) #.replace("\n", " ").strip()
            # Count the number of lines
            lines = [l.strip() for l in title.split("\n") if l.strip()]

            # If there is one line, we use it as title.
            # Otherwise we leave it to be inserted as a note.
            if len(lines) == 1:
                item.setData(Outline.title.value, "".join(lines))
                content = ""

        if content:
            # Set the note content as text value
            content = HTML2MD(content)
            item.setData(Outline.notes.value, content)

        if url:
            # Set the url in notes
            item.setData(Outline.notes.value,
                         item.data(Outline.notes.value) + "\n\n" + url)

        children = underElement.findall('node')

        # Process children
        if children is not None and len(children) > 0:
            for c in children:
                items.extend(self.parseItems(c, item))

        # Process if no children
        elif self.getSetting("importTipAs").value() == "Text":
            # Transform item to text
            item.setData(Outline.type.value, 'md')
            # Move notes to text
            if item.data(Outline.notes.value):
                item.setData(Outline.text.value, item.data(Outline.notes.value))
                item.setData(Outline.notes.value, "")

        return items
