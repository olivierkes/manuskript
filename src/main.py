# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("Theologeek")
    app.setOrganizationDomain("www.theologeek.ch")
    app.setApplicationName("snowFlaqe")

    
    from mainWindow import MainWindow
    
    
    main = MainWindow()
    main.show()
    
    app.exec_()
    app.deleteLater()
