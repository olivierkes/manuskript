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

def launch(app, MW = None):
    if MW is None:
        from manuskript.functions import mainWindow
        MW = mainWindow()

    MW.show()

    # Support for IPython Jupyter QT Console as a debugging aid.
    # Last argument must be --console to enable it
    # Code reference : 
    # https://github.com/ipython/ipykernel/blob/master/examples/embedding/ipkernel_qtapp.py
    # https://github.com/ipython/ipykernel/blob/master/examples/embedding/internal_ipkernel.py
    if len(sys.argv) > 1 and sys.argv[-1] == "--console":
        try:
            from IPython.lib.kernel import connect_qtconsole
            from ipykernel.kernelapp import IPKernelApp
            # Only to ensure matplotlib QT mainloop integration is available
            import matplotlib

            # Create IPython kernel within our application
            kernel = IPKernelApp.instance()
            
            # Initialize it and use matplotlib for main event loop integration with QT
            kernel.initialize(['python', '--matplotlib=qt'])

            # Create the console in a new process and connect
            console = connect_qtconsole(kernel.abs_connection_file, profile=kernel.profile)

            # Export MW and app variable to the console's namespace
            kernel.shell.user_ns['MW'] = MW
            kernel.shell.user_ns['app'] = app
            kernel.shell.user_ns['kernel'] = kernel
            kernel.shell.user_ns['console'] = console

            # When we close manuskript, make sure we close the console process and stop the
            # IPython kernel's mainloop, otherwise the app will never finish.
            def console_cleanup():
                app.quit()
                console.kill()
                kernel.io_loop.stop()
            app.lastWindowClosed.connect(console_cleanup)

            # Very important, IPython-specific step: this gets GUI event loop
            # integration going, and it replaces calling app.exec_()
            kernel.start()
        except Exception as e:
            print("Console mode requested but error initializing IPython : %s" % str(e))
            print("To make use of the Interactive IPython QT Console, make sure you install : ")
            print("$ pip3 install ipython qtconsole matplotlib")
            qApp.exec_()
    else:
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
    launch(app, MW)

if __name__ == "__main__":
    run()
