#!/usr/bin/env python
#--!-- coding: utf8 --!--

import collections
from qt import *
from .html import htmlExporter
from .arbo import arboExporter
from .odt import odtExporter

formats = collections.OrderedDict([
    #Format
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
    ('odt',  (
        qApp.translate("exporter", "OpenDocument (LibreOffice)"), 
        odtExporter,
        qApp.translate("exporter", "OpenDocument (*.odt)"))),
    ('epub', (
        "ePub (not yet)", 
        None,
        None)),
])