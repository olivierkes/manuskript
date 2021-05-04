#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.io.textFile import TextFile
from manuskript.io.jsonFile import JsonFile
from manuskript.io.xmlFile import XmlFile
from manuskript.io.opmlFile import OpmlFile
from manuskript.io.plotsFile import PlotsFile

extensions = {
    ".txt": TextFile,
    ".json": JsonFile,
    ".xml": XmlFile,
    ".opml": OpmlFile
}
