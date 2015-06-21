# -*- coding: utf-8 -*-

import sys
from qt import *

_version = "0.1"

import faulthandler
faulthandler.enable()

def run():
    app = QApplication(sys.argv)
    app.setOrganizationName("manuskript")
    app.setOrganizationDomain("www.theologeek.ch")
    app.setApplicationName("manuskript")
    app.setApplicationVersion("0.1")
    
    app.setStyle("Fusion")
    
    ### Translation process
    locale = QLocale.system().name()
    locale = "fr_CH"
    #qtTranslator = QTranslator()
    #if qtTranslator.load("qt_" + locale):
        #app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    if appTranslator.load("i18n/manuskript_{}.qm".format(locale)):
        app.installTranslator(appTranslator)
        print(app.tr("Loaded transation: {}.").format(locale))
    else:
        print(app.tr("Failed to load translator for {}...").format(locale))
    
    # Load style from QSettings
    settings = QSettings(app.organizationName(), app.applicationName())
    if settings.contains("applicationStyle"):
        style = settings.value("applicationStyle")
        app.setStyle(style)
    
    launch() # Seperating launch to avoid segfault, so it seem.
             # Cf. http://stackoverflow.com/questions/12433491/is-this-pyqt-4-python-bug-or-wrongly-behaving-code
    
def launch():
    from mainWindow import MainWindow
    
    main = MainWindow()
    main.show()
    
    qApp.exec_()
    qApp.deleteLater()
    

if __name__ == "__main__":
        
    run()