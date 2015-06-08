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
    #qtTranslator = QTranslator()
    #if qtTranslator.load("qt_" + locale):
        #app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    if appTranslator.load("languages/snowflaQe_{}".format(locale)):
        app.installTranslator(appTranslator)
    else:
        print("Failed to load translator...")
    
    
    from mainWindow import MainWindow
    
    
    main = MainWindow()
    main.show()
    
    app.exec_()
    app.deleteLater()

if __name__ == "__main__":
    run()