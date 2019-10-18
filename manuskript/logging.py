# -*- coding: utf-8 -*-

# While all logging should be done through the facilities offered by the
# standard python `logging` module, this module will take care of specific
# manuskript needs to keep it separate from the rest of the logic.

import os
import logging

from manuskript.functions import writablePath
from importlib import  import_module

LOGGER = logging.getLogger(__name__)

LOGFORMAT_CONSOLE = "%(levelname)s> %(message)s"
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

    LOGGER.debug("Logging to STDERR.")


def logToFile(file_level=logging.DEBUG, logfile=None):
    """Sets up the FileHandler that logs to a file.

    This is being done separately due to relying on QApplication being properly
    configured; without it we cannot detect the proper location for the log file.

    To log file: >DEBUG, timestamped.    (All the details.)"""

    if logfile is None:
        logfile = os.path.join(writablePath(), "manuskript.log")

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


# Qt has its own logging facility that we would like to integrate into our own.
# See: http://thispageintentionally.blogspot.com/2014/03/trapping-qt-log-messages.html

from PyQt5.QtCore import qInstallMessageHandler, QLibraryInfo, QMessageLogContext
from PyQt5.Qt import QtMsgType

def qtMessageHandler(msg_type, msg_log_context, msg_string):
    """Forwards Qt messages to Python logging system."""
    # Convert Qt msg type to logging level
    log_level = [logging.DEBUG,
                 logging.WARNING,
                 logging.ERROR,
                 logging.FATAL] [ int(msg_type) ]
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

import pathlib

def logVersionInformation(logger=None):
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
