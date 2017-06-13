#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings

from manuskript.functions import appPath


class PDFViewer(QWebEngineView):
    pdf_viewer_page = "file://"+appPath('libs/pdf.js/web/viewer.html')

    def __init__(self, parent=None):
        QWebEngineView.__init__(self, parent)
        self.settings = QWebEngineSettings.globalSettings()
        self.settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

    def loadPDF(self, pdf):
        url = QUrl(self.pdf_viewer_page+"?file="+pdf)
        self.settings.clearMemoryCaches()
        self.load(url)
