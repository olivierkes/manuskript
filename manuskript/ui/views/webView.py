#!/usr/bin/env python
# --!-- coding: utf8 --!--
import os

features = {'qtwebkit': False, 'qtwebengine': False}

if 'QT_WEB' in os.environ:
    features[os.environ['QT_WEB']] = True
else:
    try:
        import PyQt6.QtWebKitWidgets
        features['qtwebkit'] = True
    except:
        features['qtwebkit'] = False

    try:
        import PyQt6.QtWebEngineWidgets
        features['qtwebengine'] = True
    except:
        features['qtwebengine'] = False

if features['qtwebkit']:
    from PyQt6.QtWebKitWidgets import QWebView
    webEngine = "QtWebKit"
    webView = QWebView
elif features['qtwebengine']:
    from PyQt6 import QtWebEngineWidgets
    webEngine = "QtWebEngine"
    webView = QtWebEngineWidgets.QWebEngineView
else:
    from PyQt6.QtWidgets import QTextEdit
    webEngine = "QTextEdit"
    webView = QTextEdit
