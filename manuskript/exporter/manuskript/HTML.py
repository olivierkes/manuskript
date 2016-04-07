#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import Qt
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QPlainTextEdit, qApp, QTabWidget, QFrame

from manuskript.exporter.manuskript.markdown import markdown
from manuskript.ui.exporters.manuskript.plainTextSettings import exporterSettings

try:
    import markdown as MD
except ImportError:
    MD = None

class HTML(markdown):
    name = "HTML"
    description = qApp.translate("Export", "Basic HTML output using python module 'markdown'.")
    InvalidBecause = qApp.translate("Export", "python module 'markdown'.")

    @classmethod
    def isValid(cls):
        return MD is not None

    @classmethod
    def settingsWidget(cls):
        w = exporterSettings(cls)
        w.loadSettings()
        return w

    @classmethod
    def previewWidget(cls):
        t = QTabWidget()
        t.setDocumentMode(True)
        t.setStyleSheet("""
            QTabBar::tab{
                background-color: #BBB;
                padding: 2px;
                border: none;
                width: 100%;
            }

            QTabBar::tab:selected, QToolBox::tab:hover{
                background-color:skyblue;
            }
        """)
        w1 = QPlainTextEdit()
        w1.setFrameShape(QFrame.NoFrame)
        w1.setReadOnly(True)
        w2 = QWebView()
        t.addTab(w2, qApp.translate("Export", "HTML"))
        t.addTab(w1, qApp.translate("Export", "Source"))
        return t

    @classmethod
    def preview(cls, settingsWidget, previewWidget):
        settings = settingsWidget.getSettings()

        # Save settings
        settingsWidget.writeSettings()

        src = markdown.output(settings)
        html = MD.markdown(src)

        cls.preparesTextEditView(previewWidget.widget(1), settings["Preview"]["PreviewFont"])
        previewWidget.widget(1).setPlainText(html)
        previewWidget.widget(0).setHtml(html)



