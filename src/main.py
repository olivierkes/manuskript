# -*- coding: utf-8 -*-

import sys
from qt import *


def run():
    app = QApplication(sys.argv)
    app.setOrganizationName("Theologeek")
    app.setOrganizationDomain("www.theologeek.ch")
    app.setApplicationName("snowFlaqe")

    app.setStyle("Fusion")
    
    ### Translation process
    locale = QLocale.system().name()
    locale = "fr_CH"
    #qtTranslator = QTranslator()
    #if qtTranslator.load("qt_" + locale):
        #app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    if appTranslator.load("i18n/snowflaQe_{}.qm".format(locale)):
        app.installTranslator(appTranslator)
        print(app.tr("Loaded transation: {}.").format(locale))
    else:
        print(app.tr("Failed to load translator for {}...").format(locale))
    
    from mainWindow import MainWindow
    
    
    main = MainWindow()
    main.show()
    
    app.exec_()
    app.deleteLater()

if __name__ == "__main__":
    run()