#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.exporter.manuskript import manuskriptExporter
from manuskript.exporter.mmd import mmdExporter
from manuskript.exporter.pandoc import pandocExporter

exporters = [
    manuskriptExporter(),
    pandocExporter(),
    mmdExporter()
]

def getExporterByName(name):
    for e in exporters:
        if e.name == name:
            return e

    return None