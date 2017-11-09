#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.importer.abstractImporter import abstractImporter
from manuskript.models.outlineModel import outlineItem
from manuskript.enums import Outline
from PyQt5.QtWidgets import qApp
import re, os


class markdownImporter(abstractImporter):

    name = "Markdown"
    description = ""
    fileFormat = "Markdown files (*.md *.txt *)"
    icon = "text-x-markdown"

    @classmethod
    def isValid(cls):
        return True

    def startImport(self, filePath, parentItem, settingsWidget, fromString=None):
        """
        Very simple import from markdown. We just look at ATX headers (we
        ignore setext for the sake of simplicity, for now.)

        **A difficulty:** in the following example, we can do things with
        markdown headers (like go from level 1 to level 4 and back to level 2)
        that we cannot do in an outline.

        ```
        # Level 1
        # Level 1
        ## Level 2
        ### Level 3
        #### Level 4
        ##### Level 5
        ### Level 3
        # Level 1
        #### Level 4? → Level 2
        ### Level 3? → Level 2
        ## Level 2 → Level 2
        #### Level 4? → Level 3
        ```

        I think the current version of the imported manages that quite well.

        **A question:** In the following sample, the first Level 1 becomes a
        text element, because it has no other sub elements. But the content of
        second Level 1 becomes a text element, with no name. What name should
        we give it?

        ```
        # Level 1
        Some texte content.
        Level 1 will become a text element.
        # Level 1
        This content has no name.
        ## Level 2
        ...
        ```
        """

        if not fromString:
            # Read file
            with open(filePath, "r") as f:
                txt = f.read()
        else:
            txt = fromString

        items = []

        parent = parentItem
        lastLevel = 0
        content = ""

        def saveContent(content, parent):
            if content.strip():
                child = outlineItem(title=parent.title(), parent=parent, _type="md")
                child._data[Outline.text] = content
                items.append(child)
            return ""

        def addTitle(name, parent, level):
            child = outlineItem(title=name, parent=parent)
            child.__miLevel = level
            items.append(child)
            return child

        ATXHeader = re.compile(r"(\#+)\s*(.+?)\s*\#*$")
        setextHeader1 = re.compile(r"([^\#-=].+)\n(===+)$", re.MULTILINE)
        setextHeader2 = re.compile(r"([^\#-=].+)\n(---+)$", re.MULTILINE)

        # We store the level of each item in a temporary var
        parent.__miLevel = 0  # markdown importer header level

        txt = txt.split("\n")
        skipNextLine = False
        for i in range(len(txt)):

            l = txt[i]
            l2 = "\n".join(txt[i:i+2])

            header = False

            if skipNextLine:
                # Last line was a setext-style header.
                skipNextLine = False
                continue

            # Check ATX Header
            m = ATXHeader.match(l)
            if m:
                header = True
                level = len(m.group(1))
                name = m.group(2)

            # Check setext header
            m = setextHeader1.match(l2)

            if not header and m and len(m.group(1)) == len(m.group(2)):
                header = True
                level = 1
                name = m.group(1)
                skipNextLine = True

            m = setextHeader2.match(l2)
            if not header and m and len(m.group(1)) == len(m.group(2)):
                header = True
                level = 2
                name = m.group(1)
                skipNextLine = True

            if header:

                # save content
                content = saveContent(content, parent)

                # get parent level
                while parent.__miLevel >= level:
                    parent = parent.parent()

                # create title
                child = addTitle(name, parent, level)
                child.__miLevel = level

                # title becomes the new parent
                parent = child

                lastLevel = level

            else:
                content += l + "\n"

        saveContent(content, parent)

        # Clean up
        for i in items:
            if i.childCount() == 1 and i.children()[0].isText():
                # We have a folder with only one text item
                # So we make it a text item
                i._data[Outline.type] = "md"
                i._data[Outline.text] = i.children()[0].text()
                c = i.removeChild(0)
                items.remove(c)

        return items

    def settingsWidget(self, widget):
        """
        Takes a QWidget that can be modified and must be returned.
        """

        # Add group
        group = self.addGroup(widget.toolBox.widget(0),
                              qApp.translate("Import", "Markdown import"))
        #group = cls.addPage(widget, "Folder import")

        self.addSetting("info", "label",
                        qApp.translate("Import", """<b>Info:</b> A very simple
                        parser that will go through a markdown document and
                        create items for each titles.<br/>&nbsp;"""))

        for s in self.settings:
            self.settings[s].widget(group)

        return widget
