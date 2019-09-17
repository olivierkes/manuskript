# -*- coding: utf-8 -*-

import faulthandler
import os
import platform
import sys

import manuskript.ui.views.webView
from PyQt5.QtCore import QLocale, QTranslator, QSettings, Qt
from PyQt5.QtGui import QIcon, QColor, QPalette
from PyQt5.QtWidgets import QApplication, qApp, QStyleFactory

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
    appTranslator = QTranslator(app)
    # By default: locale

    def tryLoadTranslation(translation, source):
        """Tries to load and activate a given translation for use."""
        if appTranslator.load(translation, appPath("i18n")):
            app.installTranslator(appTranslator)
            print("Loaded translation: {}".format(translation))
            # Note: QTranslator.load() does some fancy heuristics where it simplifies
            #   the given locale until it is 'close enough' if the given filename does
            #   not work out. For example, if given 'i18n/manuskript_en_US.qm', it tries:
            #      * i18n/manuskript_en_US.qm.qm
            #      * i18n/manuskript_en_US.qm
            #      * i18n/manuskript_en_US
            #      * i18n/manuskript_en.qm
            #      * i18n/manuskript_en
            #      * i18n/manuskript.qm
            #      * i18n/manuskript
            #   We have no way to determining what it eventually went with, so mind your
            #   filenames when you observe strange behaviour with the loaded translations.
            return True
        else:
            print("No translation found or loaded. ({})".format(translation))
            return False

    def activateTranslation(translation, source):
        """Loads the most suitable translation based on the available information."""
        using_builtin_translation = True

        if (translation != ""):  # empty string == 'no translation, use builtin'
            if isinstance(translation, str):
                if tryLoadTranslation(translation, source):
                    using_builtin_translation = False
            else:  # A list of language codes to try. Once something works, we're done.
                # This logic is loosely based on the working of QTranslator.load(QLocale, ...);
                # it allows us to more accurately detect the language used for the user interface.
                for language_code in translation:
                    lc = language_code.replace('-', '_')
                    if lc.lower() == 'en_US'.lower():
                        break
                    if tryLoadTranslation("manuskript_{}.qm".format(lc), source):
                        using_builtin_translation = False
                        break

        if using_builtin_translation:
            print("Using the builtin translation.")

    # Load application translation
    translation = ""
    source = "default"
    if settings.contains("applicationTranslation"):
        # Use the language configured by the user.
        translation = settings.value("applicationTranslation")
        source = "user setting"
    else:
        # Auto-detect based on system locale.
        translation = QLocale().uiLanguages()
        source = "available ui languages"

    print("Preferred translation: {} (based on {})".format(("builtin" if translation == "" else translation), source))
    activateTranslation(translation, source)

    def respectSystemDarkThemeSetting():
        """Adjusts the Qt theme to match the OS 'dark theme' setting configured by the user."""
        if platform.system() is not 'Windows':
            return

        # Basic Windows 10 Dark Theme support.
        # Source: https://forum.qt.io/topic/101391/windows-10-dark-theme/4
        themeSettings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", QSettings.NativeFormat)
        if themeSettings.value("AppsUseLightTheme") == 0:
            darkPalette = QPalette()
            darkColor = QColor(45,45,45)
            disabledColor = QColor(127,127,127)
            darkPalette.setColor(QPalette.Window, darkColor)
            darkPalette.setColor(QPalette.WindowText, Qt.GlobalColor.white)
            darkPalette.setColor(QPalette.Base, QColor(18,18,18))
            darkPalette.setColor(QPalette.AlternateBase, darkColor)
            darkPalette.setColor(QPalette.ToolTipBase, Qt.GlobalColor.white)
            darkPalette.setColor(QPalette.ToolTipText, Qt.GlobalColor.white)
            darkPalette.setColor(QPalette.Text, Qt.GlobalColor.white)
            darkPalette.setColor(QPalette.Disabled, QPalette.Text, disabledColor)
            darkPalette.setColor(QPalette.Button, darkColor)
            darkPalette.setColor(QPalette.ButtonText, Qt.GlobalColor.white)
            darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, disabledColor)
            darkPalette.setColor(QPalette.BrightText, Qt.GlobalColor.red)
            darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))

            darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            darkPalette.setColor(QPalette.HighlightedText, Qt.GlobalColor.black)
            darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, disabledColor)

            # Fixes ugly (not to mention hard to read) disabled menu items.
            # Source: https://bugreports.qt.io/browse/QTBUG-10322?focusedCommentId=371060#comment-371060
            darkPalette.setColor(QPalette.Disabled, QPalette.Light, Qt.GlobalColor.transparent)

            app.setPalette(darkPalette)

            # This broke the Settings Dialog at one point... and then it stopped breaking it.
            # TODO: Why'd it break? Check if tooltips look OK... and if not, make them look OK.
            #app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    respectSystemDarkThemeSetting()

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
