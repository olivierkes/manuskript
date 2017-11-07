#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.importer.folderImporter import folderImporter
from manuskript.importer.markdownImporter import markdownImporter
from manuskript.importer.opmlImporter import opmlImporter
from manuskript.importer.pandocImporters import markdownPandocImporter, \
    odtPandocImporter, ePubPandocImporter, docXPandocImporter, HTMLPandocImporter, \
    rstPandocImporter, LaTeXPandocImporter

importers = [
    # Internal
    opmlImporter,
    folderImporter,
    markdownImporter,

    # Pandoc
    markdownPandocImporter,
    odtPandocImporter,
    ePubPandocImporter,
    docXPandocImporter,
    HTMLPandocImporter,
    rstPandocImporter,
    LaTeXPandocImporter,
    ]
