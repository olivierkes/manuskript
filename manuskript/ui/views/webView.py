#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QTextEdit

try:
    from PyQt5.QtWebKitWidgets import QWebView
    print("Debug: Web rendering engine used: QWebView")
    webEngine = "QtWebKit"
    webView = QWebView

except:

    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        print("Debug: Web rendering engine used: QWebEngineView")
        webEngine = "QtWebEngine"
        webView = QWebEngineView

    except:
        print("Debug: Web rendering engine used: QTextEdit")
        webEngine = "QTextEdit"
        webView = QTextEdit
