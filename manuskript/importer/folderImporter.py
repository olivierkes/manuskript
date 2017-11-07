#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.importer.abstractImporter import abstractImporter


class folderImporter(abstractImporter):

    name = "Folder"
    description = ""
    fileFormat = "<<folder>>"
    icon = "folder"
