# -*- coding: utf-8 -*-

import faulthandler
import sys

from PyQt5.QtCore import QLocale, QTranslator, QSettings
from PyQt5.QtWidgets import QApplication
from .functions import *

_version = "0.1"

faulthandler.enable()


def run():
    app = QApplication(sys.argv)
    app.setOrganizationName("manuskript")
    app.setOrganizationDomain("www.theologeek.ch")
    app.setApplicationName("manuskript")
    app.setApplicationVersion(_version)

    app.setStyle("Fusion")

    # Translation process
    locale = QLocale.system().name()
    # locale = "fr_CH"

    appTranslator = QTranslator()
    if appTranslator.load(appPath("i18n/manuskript_{}.qm").format(locale)):
        app.installTranslator(appTranslator)
        print(app.tr("Loaded transation: {}.").format(locale))
    else:
        print(app.tr("Failed to load translator for {}...").format(locale))

    # Load style from QSettings
    settings = QSettings(app.organizationName(), app.applicationName())
    if settings.contains("applicationStyle"):
        style = settings.value("applicationStyle")
        app.setStyle(style)

    QIcon.setThemeSearchPaths(QIcon.themeSearchPaths() + [appPath("icons")])
    QIcon.setThemeName("NumixMsk")
    print(QIcon.hasThemeIcon("dialog-no"))
    print(QIcon.themeSearchPaths())
    # qApp.setWindowIcon(QIcon.fromTheme("im-aim"))

    # Seperating launch to avoid segfault, so it seem.
    # Cf. http://stackoverflow.com/questions/12433491/is-this-pyqt-4-python-bug-or-wrongly-behaving-code
    launch()


def launch():
    from .mainWindow import MainWindow

    main = MainWindow()
    main.show()

    qApp.exec_()
    qApp.deleteLater()


if __name__ == "__main__":
    run()
