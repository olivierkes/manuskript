# -*- coding: utf-8 -*-

import sys
from qt import *


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
