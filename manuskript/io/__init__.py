#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.io.textFile import TextFile
from manuskript.io.jsonFile import JsonFile
from manuskript.io.xmlFile import XmlFile
from manuskript.io.opmlFile import OpmlFile
from manuskript.io.mmdFile import MmdFile
from manuskript.io.zipFile import ZipFile
from manuskript.io.mskFile import MskFile


def formatByExtension(extension: str) -> str:
    formats = {
        "md": "markdown",
        "txt": "plain",
        "bbl": "bibtex",
        "tex": "latex"
    }

    if extension in formats:
        return formats[extension]
    else:
        return extension
