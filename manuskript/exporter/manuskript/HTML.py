#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QPlainTextEdit, qApp, QTabWidget, QFrame, QTextEdit

from manuskript.exporter.manuskript.markdown import markdown, markdownSettings
from manuskript.ui.views.webView import webView
from manuskript.ui.exporters.manuskript.plainTextSettings import exporterSettings
import os

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
        t.addTab(w0, qApp.translate("Export", "Markdown source"))
        t.addTab(w1, qApp.translate("Export", "HTML Source"))
        
        if webView:
            w2 = webView()
            t.addTab(w2, qApp.translate("Export", "HTML Output"))

        t.setCurrentIndex(2)
        return t

    def output(self, settingsWidget):
        html = MD.markdown(markdown.output(self, settingsWidget))
        return html

    def preview(self, settingsWidget, previewWidget):
        settings = settingsWidget.getSettings()

        # Save settings
        settingsWidget.writeSettings()

        md = markdown.output(self, settingsWidget)
        html = MD.markdown(md)
        path = os.path.join(self.projectPath(), "dummy.html")

        self.preparesTextEditView(previewWidget.widget(0), settings["Preview"]["PreviewFont"])
        self.preparesTextEditViewMarkdown(previewWidget.widget(0), settings)
        previewWidget.widget(0).setPlainText(md)
        self.preparesTextEditView(previewWidget.widget(1), settings["Preview"]["PreviewFont"])
        previewWidget.widget(1).setPlainText(html)
        w2 = previewWidget.widget(2)
        if isinstance(w2, QTextEdit):
            w2.setHtml(html)
        else:
            w2.setHtml(html, QUrl.fromLocalFile(path))
