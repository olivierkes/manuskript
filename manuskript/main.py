# -*- coding: utf-8 -*-

import faulthandler
import os
import sys

# import PyQt5.QtWebEngineWidgets # must be imported before QApplication
from PyQt5.QtCore import QLocale, QTranslator, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, qApp

from manuskript.functions import appPath, writablePath

_version = "0.4.0"

faulthandler.enable()


def run():
    app = QApplication(sys.argv)
    app.setOrganizationName("manuskript")
    app.setOrganizationDomain("www.theologeek.ch")
    app.setApplicationName("manuskript")
    app.setApplicationVersion(_version)

    print("Running manuskript version {}.".format(_version))
    icon = QIcon()
    for i in [16, 32, 64, 128, 256, 512]:
        icon.addFile(appPath("icons/Manuskript/icon-{}px.png".format(i)))
    qApp.setWindowIcon(icon)

    app.setStyle("Fusion")

    # Load style from QSettings
    settings = QSettings(app.organizationName(), app.applicationName())
    if settings.contains("applicationStyle"):
        style = settings.value("applicationStyle")
        app.setStyle(style)

    # Translation process
    locale = QLocale.system().name()

    appTranslator = QTranslator()
    # By default: locale
    translation = appPath(os.path.join("i18n", "manuskript_{}.qm".format(locale)))

    # Load translation from settings
    if settings.contains("applicationTranslation"):
        translation = appPath(os.path.join("i18n", settings.value("applicationTranslation")))
        print("Found translation in settings:", translation)

    if appTranslator.load(translation):
        app.installTranslator(appTranslator)
        print(app.tr("Loaded translation: {}.").format(translation))

    else:
        print(app.tr("Note: No translator found or loaded for locale {}.").format(locale))

    QIcon.setThemeSearchPaths(QIcon.themeSearchPaths() + [appPath("icons")])
    QIcon.setThemeName("NumixMsk")
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
