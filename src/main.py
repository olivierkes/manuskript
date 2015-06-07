# -*- coding: utf-8 -*-

import sys
from qt import *


def run():
    app = QApplication(sys.argv)
    app.setOrganizationName("Theologeek")
    app.setOrganizationDomain("www.theologeek.ch")
    app.setApplicationName("snowFlaqe")

    app.setStyle("Fusion")
    
    from mainWindow import MainWindow
    
    
    main = MainWindow()
    main.show()
    
    app.exec_()
    app.deleteLater()

if __name__ == "__main__":
    run()