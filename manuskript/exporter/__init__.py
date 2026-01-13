#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.exporter.abstractExporter import AbstractExporter
from manuskript.exporter.htmlExporter import HTMLExporter
from manuskript.exporter.markdownExporter import MarkdownExporter


__exporters__ = list(filter(lambda exporter: exporter.isValid(), [
    HTMLExporter(),
    MarkdownExporter()
]))


def getExporters() -> list:
    global __exporters__
    return __exporters__


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
