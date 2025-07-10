# -*- coding: utf-8 -*-

# While all logging should be done through the facilities offered by the
# standard python `logging` module, this module will take care of specific
# manuskript needs to keep it separate from the rest of the logic.

import os
import sys
import time
import logging
import pathlib

from manuskript.functions import writablePath
from importlib import  import_module
from pprint import pformat

LOGGER = logging.getLogger(__name__)

LOGFORMAT_CONSOLE = "%(asctime)s: %(levelname)s> %(message)s"
LOGFORMAT_FILE = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setUp(console_level=logging.WARN):
    """Sets up a convenient environment for logging.

    To console:  >WARNING, plain.        (Only the essence.)"""

    # The root_logger should merely trigger on warnings since it is the final
    # stop after all categories we really care about didn't match.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARN)
    # The manuskript_logger is what all of our own code will come by.
    # Obviously, we care greatly about logging every single message.
    manuskript_logger = logging.getLogger("manuskript")
    manuskript_logger.setLevel(logging.DEBUG)
    # The qt_logger sees all the Qt nonsense when it breaks.
    # We don't really want to know... but we have to know.
    qt_logger = logging.getLogger("qt")
    qt_logger.setLevel(logging.DEBUG)

    # Send logs of WARNING+ to STDERR for higher visibility.
    ch = logging.StreamHandler()
    ch.setLevel(console_level)
    ch.setFormatter(logging.Formatter(LOGFORMAT_CONSOLE))
    root_logger.addHandler(ch)

    # Any exceptions we did not account for need to be logged.
    logFutureExceptions()

    LOGGER.debug("Logging to STDERR.")


def getDefaultLogFile():
    """Returns a filename to log to inside {datadir}/logs/.

    It also prunes old logs so that we do not hog disk space excessively over time.
    """
    # Ensure logs directory exists.
    logsPath = os.path.join(writablePath(), "logs")
    os.makedirs(logsPath, exist_ok=True)
    # Prune irrelevant log files. They are only kept for 35 days.
    try:  # Guard against os.scandir() in the name of paranoia.
        now = time.time()
        with os.scandir(logsPath) as it:
            for f in it:
                try:  # Avoid triggering outer try-except inside loop.
                    if f.is_dir():
                        continue  # If a subdirectory exists for whatever reason, don't touch it.
                    if (now - f.stat().st_ctime) // (24 * 3600) >= 35:
                        os.remove(f)
                except OSError:
                    continue  # Fail silently, but make sure we check other files.
    except OSError:
        pass  # Fail silently. Don't explode and prevent Manuskript from starting.
    return os.path.join(logsPath, "%Y-%m-%d_%H-%M-%S_manuskript#%#.log")


def formatLogName(formatString, pid=None, now=None):
    """A minor hack on top of `strftime()` to support an identifier for the process ID.

    We want to support this in case some genius manages to start two manuskript processes
    during the exact same second, causing a conflict in log filenames.

    Additionally, there is a tiny chance that the pid could actually end up relevant when
    observing strange behaviour with a Manuskript process but having multiple instances open.
    """
    if pid == None:
        pid = os.getpid()
    if now == None:
        now = time.localtime()

    # Replace %# that is NOT preceded by %. Although this is not a perfect solution,
    # it is good enough because it is unlikely anyone would want to format '%pid'.
    lidx = 0
    while True:  # This could be neater with the := operator of Python 3.8 ...
        fidx = formatString.find("%#", lidx)
        if fidx == -1:
            break
        elif (fidx == 0) or (formatString[fidx-1] != "%"):
            formatString = formatString[:fidx] + str(pid) + formatString[fidx+2:]
            lidx = fidx + len(str(pid)) - 2
        else:  # skip and avoid endless loop
            lidx = fidx + 1

    # Finally apply strftime normally.
    return time.strftime(formatString, now)


def logToFile(file_level=logging.DEBUG, logfile=None):
    """Sets up the FileHandler that logs to a file.

    This is being done separately due to relying on QApplication being properly
    configured; without it we cannot detect the proper location for the log file.

    To log file: >DEBUG, timestamped.    (All the details.)"""

    if logfile is None:
        logfile = getDefaultLogFile()

    logfile = formatLogName(logfile)

    # Log with extreme prejudice; everything goes to the log file.
    # Because Qt gave me a megabyte-sized logfile while testing, it
    # makes sense that the default behaviour of appending to existing
    # log files may not be in our users best interest for the time
    # being. (Unfortunately.)
    try:
        fh = logging.FileHandler(logfile, mode='w', encoding='utf-8')
        fh.setLevel(file_level)
        fh.setFormatter(logging.Formatter(LOGFORMAT_FILE))

        root_logger = logging.getLogger()
        root_logger.addHandler(fh)

        # Use INFO level to make it easier to find for users.
        LOGGER.info("Logging to file: %s", logfile)
    except Exception as ex:
        LOGGER.warning("Cannot log to file '%s'. Reason: %s", logfile, ex)


def getLogFilePath():
    """Extracts a filename we are logging to from the first FileHandler we find."""
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return handler.baseFilename
    return None


# Log uncaught and unraisable exceptions.

# Uncaught exceptions trigger moments before a thread is terminated due to
# an uncaught exception. It is the final stop, and as such is very likely
# to be the reason Manuskript suddenly closed on the user without warning.
# (It can also happen on other threads, but it is a bad thing regardless!)
def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    # Allow Ctrl+C for script execution to keep functioning as-is.
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return # default exception hook handled it

    # Anything that reaches this handler can be considered a deal-breaker.
    LOGGER.critical("An unhandled exception has occurred!", exc_info=(exc_type, exc_value, exc_traceback))

    # Exit the program to preserve PyQt 'functionality' that is broken by
    # having our own uncaught exception hook. For more information, see:
    #   https://stackoverflow.com/questions/49065371/why-does-sys-excepthook-behave-differently-when-wrapped
    sys.exit(1)

    # Note that without it, unhandled Python exceptions thrown while in the
    # bowels of Qt may be written to the log multiple times. Under the motto
    # of failing fast and not having a misleading log file, this appears to
    # be the best course of action.


# The situation with threads and uncaught exceptions is fraught in peril.
# Hopefully this solves our problems on more recent versions of Python.
def handle_uncaught_thread_exception(args):
    if issubclass(exc_type, SystemExit):
        return # match behaviour of default hook, see manual

    # Anything that reaches this handler can be considered a minor deal-breaker.
    LOGGER.error("An unhandled exception has occurred in a thread: %s", repr(args.thread),
                    exc_info=(args.exc_type, args.exc_value, args.exc_traceback))


# Unraisable exceptions are exceptions that failed to be raised to a caller
# due to the nature of the exception. Examples: __del__(), GC error, etc.
# Logging these may expose bugs / errors that would otherwise go unnoticed.
def handle_unraisable_exception(unraisable):
    # Log as warning because the application is likely to limp along with
    # no serious side effects; a resource leak is the most likely.
    LOGGER.warning("%s: %s", unraisable.err_msg or "Exception ignored in", repr(unraisable.object),
                    exc_info=(unraisable.exc_type, unraisable.exc_value, unraisable.exc_traceback))


# Because we are already somewhat careful in regards to the order of code
# execution when it comes to setting up the logging environment, this has
# been put in its own function as opposed to letting a direct import handle it.
def logFutureExceptions():
    """Log all the interesting exceptions that may happen in the future."""
    sys.excepthook = handle_uncaught_exception
    try:
        import threading # threading module was optional pre-3.7
        if hasattr(threading, "excepthook"):  # Python 3.8+
            threading.excepthook = handle_uncaught_thread_exception
    except:
        pass
    if hasattr(sys, "unraisablehook"):  # Python 3.8+
        sys.unraisablehook = handle_unraisable_exception


# Qt has its own logging facility that we would like to integrate into our own.
# See: http://thispageintentionally.blogspot.com/2014/03/trapping-qt-log-messages.html

from PyQt5.QtCore import qInstallMessageHandler, QLibraryInfo, QMessageLogContext
from PyQt5.Qt import QtMsgType

def qtMessageHandler(msg_type, msg_log_context, msg_string):
    """Forwards Qt messages to Python logging system."""
    # Convert Qt msg type to logging level
    msg_type_index = int(msg_type)
    log_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]
    if (msg_type_index >= 0) and (msg_type_index < len(log_levels)):
        log_level = log_levels[msg_type_index]
    else:
        log_level = log_levels[-1]
    qtcl = logging.getLogger(msg_log_context.category or "qt.???")
    # Some information may not be available unless using a PyQt debug build.
    # See: https://www.riverbankcomputing.com/static/Docs/PyQt5/api/qtcore/qmessagelogcontext.html
    if QLibraryInfo.isDebugBuild():
        qtcl.log(logging.DEBUG,
                    ' @ {0} : {1}'.format((msg_log_context.file or "<unknown source file>"), msg_log_context.line)
                    )
        qtcl.log(logging.DEBUG,
                    ' ! {0}'.format((msg_log_context.function or "<unknown function>"))
                    )
    qtcl.log(log_level, msg_string)

def integrateQtLogging():
    """Integrates Qt logging facilities to be a part of our own."""

    # Note: the qtlogger is initialized in setUp() because it fits in
    # nicely with the initialization of the other loggers over there.
    # I also feel a lot safer this way. Qt is a curse that just keeps
    # on giving, even when it isn't actually at fault. I hate you, Qt.

    qInstallMessageHandler(qtMessageHandler)


def versionTupleToString(t):
    """A bit of generic tuple conversion code that hopefully handles all the
    different sorts of tuples we may come across while logging versions.

    None                -> "N/A"
    (,)                 -> "N/A"
    (2, 4, 6)           -> "2.4.6"
    (2, 4, "alpha", 8)  -> "2.4-alpha.8"
    """

    s = []
    if t is None or len(t) == 0:
        return "N/A"
    else:
        s.append(str(t[0]))

    def version_chunk(v):
        if isinstance(v, str):
            return "-", str(v)
        else:
            return ".", str(v)

    s.extend(f for p in t[1:] for f in version_chunk(p))
    return "".join(s)

def attributesFromOptionalModule(module, *attributes):
    """It is nice to cut down on the try-except boilerplate by
    putting this logic into its own function.

    Returns as many values as there are attributes.
    A value will be None if it failed to get the attribute."""

    assert(len(attributes) != 0)
    v = []
    try:
        m = import_module(module)

        for a in attributes:
            v.append(getattr(m, a, None))
    except ImportError:
        v.extend(None for _ in range(len(attributes)))

    if len(v) == 1:
        # Return the value directly so we can use it in an expression.
        return v[0]
    else:
        # The list is consumed as a part of the unpacking syntax.
        return v

def logRuntimeInformation(logger=None):
    """Logs all important runtime information neatly together.

    Due to the generic nature, use the manuskript logger by default."""

    if not logger:
        logger = logging.getLogger("manuskript")

    vt2s = versionTupleToString
    afom = attributesFromOptionalModule

    # Basic system information.
    from platform import python_version, platform, processor, machine
    logger.info("Operating System: %s", platform())
    logger.info("Hardware: %s / %s", machine(), processor())

    # Information about the running instance. See:
    #   https://pyinstaller.readthedocs.io/en/v3.3.1/runtime-information.html
    #   http://www.py2exe.org/index.cgi/Py2exeEnvironment
    #   https://cx-freeze.readthedocs.io/en/latest/faq.html#data-files
    frozen = getattr(sys, 'frozen', False)
    if frozen:
        logger.info("Running in a frozen (packaged) state.")
        logger.debug("* sys.frozen = %s", pformat(frozen))

        # PyInstaller, py2exe and cx_Freeze modules are not accessible while frozen,
        # so logging their version is (to my knowledge) impossible without including
        # special steps into the distribution process. But some traces do exist...
        logger.debug("* sys._MEIPASS = %s", getattr(sys, '_MEIPASS', "N/A"))  # PyInstaller bundle
        # cx_Freeze and py2exe do not appear to leave anything similar exposed.
    else:
        logger.info("Running from unpackaged source code.")

    # File not found? These bits of information might help.
    logger.debug("* sys.executable = %s", pformat(sys.executable))
    logger.debug("* sys.argv = %s", pformat(sys.argv))
    logger.debug("* sys.path = %s", pformat(sys.path))
    logger.debug("* sys.prefix = %s", pformat(sys.prefix))

    # Manuskript and Python info.
    from manuskript.functions import getGitRevisionAsString, getManuskriptPath
    from manuskript.version import getVersion
    logger.info("Manuskript %s%s (Python %s)", getVersion(),
                    getGitRevisionAsString(getManuskriptPath(), short=True),
                    python_version())

    # Installed Python packages.

    # PyQt + Qt
    from PyQt5.Qt import PYQT_VERSION_STR, qVersion
    from PyQt5.QtCore import QT_VERSION_STR
    logger.info("* PyQt %s (compiled against Qt %s)", PYQT_VERSION_STR, QT_VERSION_STR)
    logger.info("  * Qt %s (runtime)", qVersion())

    # Lxml
    # See: https://lxml.de/FAQ.html#i-think-i-have-found-a-bug-in-lxml-what-should-i-do
    from lxml import etree
    logger.info("* lxml.etree %s",                vt2s(etree.LXML_VERSION))
    logger.info("  * libxml   %s (compiled: %s)", vt2s(etree.LIBXML_VERSION), vt2s(etree.LIBXML_COMPILED_VERSION))
    logger.info("  * libxslt  %s (compiled: %s)", vt2s(etree.LIBXSLT_VERSION), vt2s(etree.LIBXSLT_COMPILED_VERSION))

    # Spellcheckers. (Optional)
    enchant_mod_ver, enchant_lib_ver = afom("enchant", "__version__", "get_enchant_version")
    if enchant_lib_ver:
        enchant_lib_ver = enchant_lib_ver()
        if isinstance(enchant_lib_ver, bytes):  # PyEnchant version < 3.0.2
            enchant_lib_ver = enchant_lib_ver.decode('utf-8')
    logger.info("* pyEnchant %s (libenchant: %s)", enchant_mod_ver or "N/A", enchant_lib_ver or "N/A")

    logger.info("* pySpellChecker %s", afom("spellchecker", "__version__") or "N/A")
    logger.info("* Symspellpy %s", afom("symspellpy", "__version__") or "N/A")

    # Markdown. (Optional)
    logger.info("* Markdown %s", afom("markdown", "__version__") or "N/A")

    # Web rendering engine
    from manuskript.ui.views.webView import webEngine
    logger.info("Web rendering engine: %s", webEngine)

    # Do not collect version information for Pandoc; that would require
    # executing `pandov -v` and parsing the output, all of which is too slow.
