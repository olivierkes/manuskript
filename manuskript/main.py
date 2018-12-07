# -*- coding: utf-8 -*-

import faulthandler
import os
import sys

import manuskript.ui.views.webView
from PyQt5.QtCore import QLocale, QTranslator, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, qApp

from manuskript.functions import appPath, writablePath
from manuskript.version import getVersion

faulthandler.enable()

def prepare(tests=False):
    app = QApplication(sys.argv)
    app.setOrganizationName("manuskript"+("_tests" if tests else ""))
    app.setOrganizationDomain("www.theologeek.ch")
    app.setApplicationName("manuskript"+("_tests" if tests else ""))
    app.setApplicationVersion(getVersion())

    print("Running manuskript version {}.".format(getVersion()))
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

    appTranslator = QTranslator(app)
    # By default: locale

    def extractLocale(filename):
        # len("manuskript_") = 13, len(".qm") = 3
        return filename[11:-3] if len(filename) >= 16 else ""

    def tryLoadTranslation(translation, source):
        if appTranslator.load(appPath(os.path.join("i18n", translation))):
            app.installTranslator(appTranslator)
            print(app.tr("Loaded translation from {}: {}.").format(source, translation))
            return True
        else:
            print(app.tr("Note: No translator found or loaded from {} for locale {}.").
                  format(source, extractLocale(translation)))
            return False

    # Load translation from settings
    translation = ""
    if settings.contains("applicationTranslation"):
        translation = settings.value("applicationTranslation")
        print("Found translation in settings:", translation)

    if (translation != "" and not tryLoadTranslation(translation, "settings")) or translation == "":
        # load from settings failed or not set, fallback
        translation = "manuskript_{}.qm".format(locale)
        tryLoadTranslation(translation, "system locale")

    QIcon.setThemeSearchPaths(QIcon.themeSearchPaths() + [appPath("icons")])
    QIcon.setThemeName("NumixMsk")

    # Font siue
    if settings.contains("appFontSize"):
        f = qApp.font()
        f.setPointSize(settings.value("appFontSize", type=int))
        app.setFont(f)

    # Main window
    from manuskript.mainWindow import MainWindow

    MW = MainWindow()
    # We store the system default cursor flash time to be able to restore it
    # later if necessary
    MW._defaultCursorFlashTime = qApp.cursorFlashTime()

    # Command line project
    if len(sys.argv) > 1 and sys.argv[1][-4:] == ".msk":
        if os.path.exists(sys.argv[1]):
            path = os.path.abspath(sys.argv[1])
            MW._autoLoadProject = path

    return app, MW

def launch(MW = None):
    if MW is None:
        from manuskript.functions import mainWindow
        MW = mainWindow()

    MW.show()

    qApp.exec_()
    qApp.deleteLater()

def run():
    """
    Run separates prepare and launch for two reasons:
    1. I've read somewhere it helps with potential segfault (see comment below)
    2. So that prepare can be used in tests, without running the whole thing
    """
    # Need to return and keep `app` otherwise it gets deleted.
    app, MW = prepare()
    # Separating launch to avoid segfault, so it seem.
    # Cf. http://stackoverflow.com/questions/12433491/is-this-pyqt-4-python-bug-or-wrongly-behaving-code
    launch(MW)

if __name__ == "__main__":
    run()
