# -*- coding: utf-8 -*-

import faulthandler
import os
import platform
import sys
import signal

import manuskript.logging
from PyQt5.QtCore import QLocale, QTranslator, QSettings, Qt
from PyQt5.QtGui import QIcon, QColor, QPalette
from PyQt5.QtWidgets import QApplication, qApp, QStyleFactory

from manuskript.functions import appPath, writablePath
from manuskript.version import getVersion

faulthandler.enable()

import logging
LOGGER = logging.getLogger(__name__)

def prepare(arguments, tests=False):
    # Qt WebEngine demands this attribute be set _before_ we create our QApplication object.
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

    # Create the foundation that provides our Qt application with its event loop.
    app = QApplication(sys.argv)
    app.setOrganizationName("manuskript" + ("_tests" if tests else ""))
    app.setOrganizationDomain("www.theologeek.ch")
    app.setApplicationName("manuskript" + ("_tests" if tests else ""))
    app.setApplicationVersion(getVersion())

    # Beginning logging to a file. This cannot be done earlier due to the
    # default location of the log file being dependent on QApplication.
    manuskript.logging.logToFile(logfile=arguments.logfile)

    # Handle all sorts of Qt logging messages in Python.
    manuskript.logging.integrateQtLogging()

    # Log all the versions for less headaches.
    manuskript.logging.logRuntimeInformation()

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
            LOGGER.info("Loaded translation: {}".format(translation))
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
            LOGGER.info("No translation found or loaded. ({})".format(translation))
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
            LOGGER.info("Using the builtin translation. (U.S. English)")

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

    LOGGER.info("Preferred translation: {} (based on {})".format(("builtin" if translation == "" else translation), source))
    activateTranslation(translation, source)

    def respectSystemDarkThemeSetting():
        """Adjusts the Qt theme to match the OS 'dark theme' setting configured by the user."""
        if platform.system() != 'Windows':
            return

        # Basic Windows 10 Dark Theme support.
        # Source: https://forum.qt.io/topic/101391/windows-10-dark-theme/4
        themeSettings = QSettings(
            "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
            QSettings.NativeFormat)
        if themeSettings.value("AppsUseLightTheme") == 0:
            darkPalette = QPalette()
            darkColor = QColor(45, 45, 45)
            disabledColor = QColor(127, 127, 127)
            darkPalette.setColor(QPalette.Window, darkColor)
            darkPalette.setColor(QPalette.WindowText, Qt.white)
            darkPalette.setColor(QPalette.Base, QColor(18, 18, 18))
            darkPalette.setColor(QPalette.AlternateBase, darkColor)
            darkPalette.setColor(QPalette.ToolTipBase, Qt.white)
            darkPalette.setColor(QPalette.ToolTipText, Qt.white)
            darkPalette.setColor(QPalette.Text, Qt.white)
            darkPalette.setColor(QPalette.Disabled, QPalette.Text, disabledColor)
            darkPalette.setColor(QPalette.Button, darkColor)
            darkPalette.setColor(QPalette.ButtonText, Qt.white)
            darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, disabledColor)
            darkPalette.setColor(QPalette.BrightText, Qt.red)
            darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))

            darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            darkPalette.setColor(QPalette.HighlightedText, Qt.black)
            darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, disabledColor)

            # Fixes ugly (not to mention hard to read) disabled menu items.
            # Source: https://bugreports.qt.io/browse/QTBUG-10322?focusedCommentId=371060#comment-371060
            darkPalette.setColor(QPalette.Disabled, QPalette.Light, Qt.transparent)

            app.setPalette(darkPalette)

            # This broke the Settings Dialog at one point... and then it stopped breaking it.
            # TODO: Why'd it break? Check if tooltips look OK... and if not, make them look OK.
            # app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    respectSystemDarkThemeSetting()

    QIcon.setThemeSearchPaths(QIcon.themeSearchPaths() + [appPath("icons")])
    QIcon.setThemeName("NumixMsk")

    # Font size
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
    if arguments.filename is not None and arguments.filename[-4:] == ".msk":
        # The file is verified to already exist during argument parsing.
        # Our ".msk" check has been moved there too for better feedback,
        # but leaving it here to err on the side of caution.
        path = os.path.abspath(arguments.filename)
        MW._autoLoadProject = path

    return app, MW

def launch(arguments, app, MW = None):
    if MW == None:
        from manuskript.functions import mainWindow
        MW = mainWindow()

    MW.show()

    # Support for IPython Jupyter QT Console as a debugging aid.
    # Last argument must be --console to enable it
    # Code reference :
    # https://github.com/ipython/ipykernel/blob/master/examples/embedding/ipkernel_qtapp.py
    # https://github.com/ipython/ipykernel/blob/master/examples/embedding/internal_ipkernel.py
    if arguments.console:
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


def sigint_handler(sig, MW):
    def handler(*args):
        # Log before winding down to preserve order of cause and effect.
        LOGGER.info(f'{sig} received. Quitting...')
        MW.close()
        print(f'{sig} received, quit.')

    return handler


def setup_signal_handlers(MW):
    signal.signal(signal.SIGINT, sigint_handler("SIGINT", MW))
    signal.signal(signal.SIGTERM, sigint_handler("SIGTERM", MW))


def is_valid_project(parser, arg):
    if arg[-4:] != ".msk":
        parser.error("only manuskript projects (.msk) are supported!")
    if not os.path.isfile(arg):
        parser.error("the project %s does not exist!" % arg)
    else:
        return arg


def process_commandline(argv):
    import argparse
    parser = argparse.ArgumentParser(description="Run the manuskript application.")
    parser.add_argument("--console", help="open the IPython Jupyter QT Console as a debugging aid",
                        action="store_true")
    parser.add_argument("-v", "--verbose", action="count", default=1, help="lower the threshold for messages logged to the terminal")
    parser.add_argument("-L", "--logfile", default=None, help="override the default log file location")
    parser.add_argument("filename", nargs="?", metavar="FILENAME", help="the manuskript project (.msk) to open",
                        type=lambda x: is_valid_project(parser, x))

    args = parser.parse_args(args=argv)

    # Verbosity logic, see: https://gist.github.com/ms5/9f6df9c42a5f5435be0e
    #args.verbose = 70 - (10*args.verbose) if args.verbose > 0 else 0

    # Users cannot report what they do not notice: show CRITICAL, ERROR and WARNING always.
    # Note that the default is set to 1, so account for that.
    args.verbose = 40 - (10*args.verbose) if args.verbose > 0 else 0

    return args


def run():
    """
    Run separates prepare and launch for two reasons:
    1. I've read somewhere it helps with potential segfault (see comment below)
    2. So that prepare can be used in tests, without running the whole thing
    """
    # Parse command-line arguments.
    arguments = process_commandline(sys.argv[1:])
    # Initialize logging. (Does not include Qt integration yet.)
    manuskript.logging.setUp(console_level=arguments.verbose)

    # Need to return and keep `app` otherwise it gets deleted.
    app, MW = prepare(arguments)
    setup_signal_handlers(MW)
    # Separating launch to avoid segfault, so it seem.
    # Cf. http://stackoverflow.com/questions/12433491/is-this-pyqt-4-python-bug-or-wrongly-behaving-code
    launch(arguments, app, MW)


if __name__ == "__main__":
    run()
