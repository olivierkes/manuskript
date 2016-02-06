#!/usr/bin/env python
# --!-- coding: utf8 --!--
import collections

from PyQt5.QtWidgets import qApp

from manuskript.exporter.arbo import arboExporter
from manuskript.exporter.html import htmlExporter
from manuskript.exporter.odt import odtExporter

formats = collections.OrderedDict([
    # Format
    # Readable name
    # Class
    # QFileDialog filter
    ('html', (
        qApp.translate("exporter", "HTML"),
        htmlExporter,
        qApp.translate("exporter", "HTML Document (*.html)"))),
    ('arbo', (
        qApp.translate("exporter", "Arborescence"),
        arboExporter,
        None)),
    ('odt', (
        qApp.translate("exporter", "OpenDocument (LibreOffice)"),
        odtExporter,
        qApp.translate("exporter", "OpenDocument (*.odt)"))),
    ('epub', (
        "ePub (not yet)",
        None,
        None)),
])
