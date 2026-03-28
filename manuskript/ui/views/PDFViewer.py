#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QLabel
from manuskript.ui.views.webView import webView, webEngine

from manuskript.functions import appPath


if webEngine == "QtWebKit":

    from PyQt6.QtWebKit import QWebSettings
    from PyQt6.QtWebKitWidgets import QWebView


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


elif webEngine == "QtWebEngine":

    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
    except ImportError:
        from PyQt6.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings


    class PDFViewer(QWebEngineView):
        pdf_viewer_page = "file://"+appPath('libs/pdf.js/web/viewer.html')

        def __init__(self, parent=None):
            QWebEngineView.__init__(self, parent)
            self.settings = QWebEngineSettings.globalSettings()
            self.settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

        def loadPDF(self, pdf):
            url = QUrl(self.pdf_viewer_page+"?file="+pdf)
            self.load(url)


else:

    class PDFViewer(QLabel):
        def __init__(self, parent=None):
            QLabel.__init__(self, parent)
            self.setText("No Web Engine installed capable of displaying PDF.\n\n"
                         "Consider installing QtWebKit or QtWebEngine.")

        def loadPDF(self, pdf):
            pass
