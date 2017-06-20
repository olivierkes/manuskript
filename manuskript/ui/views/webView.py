#!/usr/bin/env python
# --!-- coding: utf8 --!--
import PyQt5
import os

features = {'qtwebkit': False, 'qtwebengine': False}

if 'QT_WEB' in os.environ:
    features[os.environ['QT_WEB']] = True
else:
    try:
        import PyQt5.QtWebKitWidgets
        features['qtwebkit'] = True
    except:
        features['qtwebkit'] = False

    try:
        import PyQt5.QtWebEngineWidgets
        features['qtwebengine'] = True
    except:
        features['qtwebengine'] = False

if features['qtwebkit']:
    from PyQt5.QtWebKitWidgets import QWebView
    print("Debug: Web rendering engine used: QWebView")
    webEngine = "QtWebKit"
    webView = QWebView
elif features['qtwebengine']:
    from PyQt5 import QtWebEngineWidgets
    print("Debug: Web rendering engine used: QWebEngineView")
    webEngine = "QtWebEngine"
    webView = QtWebEngineWidgets.QWebEngineView
else:
    from PyQt5.QtWidgets import QTextEdit
    print("Debug: Web rendering engine used: QTextEdit")
    webEngine = "QTextEdit"
    webView = QTextEdit
