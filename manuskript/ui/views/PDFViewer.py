#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtWebKitWidgets import QWebView, QWebPage

from manuskript.functions import appPath


class PDFViewer(QWebView):
    pdf_viewer_page = "file://"+appPath('libs/pdf.js/web/viewer.html')

    def __init__(self, parent=None):
        QWebView.__init__(self, parent)
        self.settings = QWebSettings.globalSettings()
        self.settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)

    def loadPDF(self, pdf):
        url = QUrl(self.pdf_viewer_page+"?file="+pdf)
        self.settings.clearMemoryCaches()
        self.load(url)