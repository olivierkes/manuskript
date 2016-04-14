#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QPlainTextEdit, qApp, QTabWidget, QFrame

from manuskript.exporter.manuskript.markdown import markdown, markdownSettings
from manuskript.ui.exporters.manuskript.plainTextSettings import exporterSettings

try:
    import markdown as MD
except ImportError:
    MD = None

class HTML(markdown):
    name = "HTML"
    description = qApp.translate("Export", "Basic HTML output using python module 'markdown'.")
    InvalidBecause = qApp.translate("Export", "python module 'markdown'.")
    icon = "text-html"

    exportVarName = "lastManuskriptHTML"
    exportFilter = "HTML files (*.html);; Any files (*)"

    def isValid(self):
        return MD is not None

    def settingsWidget(self):
        w = markdownSettings(self)
        w.loadSettings()
        return w

    def previewWidget(self):
        t = QTabWidget()
        t.setDocumentMode(True)
        t.setStyleSheet("""
            QTabBar::tab{
                background-color: #BBB;
                padding: 3px 25px;
                border: none;
            }

            QTabBar::tab:selected, QTabBar::tab:hover{
                background-color:skyblue;
            }
        """)
        w0 = QPlainTextEdit()
        w0.setFrameShape(QFrame.NoFrame)
        w0.setReadOnly(True)
        w1 = QPlainTextEdit()
        w1.setFrameShape(QFrame.NoFrame)
        w1.setReadOnly(True)
        w2 = QWebView()
        t.addTab(w0, qApp.translate("Export", "Markdown source"))
        t.addTab(w1, qApp.translate("Export", "HTML Source"))
        t.addTab(w2, qApp.translate("Export", "HTML Output"))

        t.setCurrentIndex(2)
        return t

    def output(self, settings):
        html = MD.markdown(markdown.output(self, settings))
        return html

    def preview(self, settingsWidget, previewWidget):
        settings = settingsWidget.getSettings()

        # Save settings
        settingsWidget.writeSettings()

        md = markdown.output(self, settings)
        html = MD.markdown(md)

        self.preparesTextEditView(previewWidget.widget(0), settings["Preview"]["PreviewFont"])
        self.preparesTextEditViewMarkdown(previewWidget.widget(0), settings)
        previewWidget.widget(0).setPlainText(md)
        self.preparesTextEditView(previewWidget.widget(1), settings["Preview"]["PreviewFont"])
        previewWidget.widget(1).setPlainText(html)
        previewWidget.widget(2).setHtml(html)



