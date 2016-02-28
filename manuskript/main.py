# -*- coding: utf-8 -*-

import faulthandler
import sys

from PyQt5.QtCore import QLocale, QTranslator, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, qApp

from manuskript.functions import appPath

_version = "0.2.0"

faulthandler.enable()


def run():
    app = QApplication(sys.argv)
    app.setOrganizationName("manuskript")
    app.setOrganizationDomain("www.theologeek.ch")
    app.setApplicationName("manuskript")
    app.setApplicationVersion(_version)

    icon = QIcon()
    for i in [16, 31, 64, 128, 256, 512]:
        icon.addFile(appPath("icons/Manuskript/icon-{}px.png".format(i)))
    qApp.setWindowIcon(icon)

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
