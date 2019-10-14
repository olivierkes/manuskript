# -*- coding: utf-8 -*-

# While all logging should be done through the facilities offered by the
# standard python `logging` module, this module will take care of specific
# manuskript needs to keep it separate from the rest of the logic.

from manuskript.functions import writablePath
import os
import logging

LOGFORMAT_CONSOLE = "%(levelname)s> %(message)s"
LOGFORMAT_FILE = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logger = logging.getLogger(__name__)

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

    logger.debug("Logging to STDERR.")


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
        fh = logging.FileHandler(logfile, mode='w')
        fh.setLevel(file_level)
        fh.setFormatter(logging.Formatter(LOGFORMAT_FILE))

        root_logger = logging.getLogger()
        root_logger.addHandler(fh)

        # Use INFO level to make it easier to find for users.
        logger.info("Logging to file: %s", logfile)
    except Exception as ex:
        logger.warning("Cannot log to file '%s'. Reason: %s", logfile, ex)


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