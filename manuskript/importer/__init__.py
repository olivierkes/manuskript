#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.importer.folderImporter import folderImporter
from manuskript.importer.markdownImporter import markdownImporter
from manuskript.importer.opmlImporter import opmlImporter

importers = [
    markdownImporter,
    opmlImporter,
    folderImporter,
    ]
