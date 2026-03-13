#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.exporter.abstractExporter import AbstractExporter
from manuskript.exporter.htmlExporter import HTMLExporter
from manuskript.exporter.latexExporter import LaTeXExporter
from manuskript.exporter.markdownExporter import MarkdownExporter
from manuskript.exporter.pdfExporter import PDFExporter


__exporters__ = [
    HTMLExporter(),
    LaTeXExporter(),
    MarkdownExporter(),
    PDFExporter(),
]


def getExporters() -> list:
    global __exporters__
    return filter(lambda exporter: exporter.isValid(), __exporters__)


def getExporterByFormat(outputFormat: str) -> AbstractExporter | None:
    for exporter in getExporters():
        if exporter.exportFormat == outputFormat:
            return exporter

    return None


def getExporterByName(name: str) -> AbstractExporter | None:
    for exporter in getExporters():
        if exporter.getName() == name:
            return exporter

    return None


def registerExporter(exporter: AbstractExporter) -> bool:
    global __exporters__

    if not exporter.isValid():
        return False
    
    if exporter in __exporters__:
        return False
    
    __exporters__.append(exporter)
    return True


def unregisterExporter(exporter: AbstractExporter) -> bool:
    global __exporters__

    if not exporter in __exporters__:
        return False
    
    __exporters__.remove(exporter)
    return True
