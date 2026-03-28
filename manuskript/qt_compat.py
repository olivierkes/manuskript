#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Compatibility layer for PyQt5 / PyQt6.

Abstracts the differences so the rest of the codebase can use a single
import style.  PyQt6 is preferred (Wayland support, scoped enums); PyQt5
is the fallback.
"""

import os
import logging

LOGGER = logging.getLogger(__name__)

###############################################################################
#  Detect available binding
###############################################################################
QT_VERSION = 0

try:
    from PyQt6 import QtCore, QtGui, QtWidgets, QtPrintSupport  # noqa: F401
    from PyQt6 import sip  # noqa: F401
    QT_VERSION = 6
    LOGGER.info("Using PyQt6 (%s)", QtCore.PYQT_VERSION_STR)
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport  # noqa: F401
    from PyQt5 import sip  # noqa: F401
    QT_VERSION = 5
    LOGGER.info("Using PyQt5 (%s)", QtCore.PYQT_VERSION_STR)


def qApp():
    """Return the current QApplication instance (works on both Qt5/6)."""
    return QtWidgets.QApplication.instance()


###############################################################################
#  PyQt6 compatibility patches
###############################################################################
if QT_VERSION == 6:
    QAction = QtGui.QAction
    QtWidgets.QAction = QtGui.QAction
    QtWidgets.QActionGroup = QtGui.QActionGroup
    QtWidgets.QShortcut = QtGui.QShortcut

    # QSignalMapper.mapped -> mappedInt
    if not hasattr(QtCore.QSignalMapper, 'mapped'):
        QtCore.QSignalMapper.mapped = property(lambda self: self.mappedInt)

    # QFontMetrics.width() -> horizontalAdvance()
    # Direct assignment fails with sip bindings; wrapper needed.
    if not hasattr(QtGui.QFontMetrics, 'width'):
        QtGui.QFontMetrics.width = lambda self, *a, **kw: self.horizontalAdvance(*a, **kw)
    if not hasattr(QtGui.QFontMetricsF, 'width'):
        QtGui.QFontMetricsF.width = lambda self, *a, **kw: self.horizontalAdvance(*a, **kw)

    # QMouseEvent: pos()/globalPos() -> position()/globalPosition()
    if not hasattr(QtGui.QMouseEvent, 'pos'):
        QtGui.QMouseEvent.pos = lambda self: self.position().toPoint()
    if not hasattr(QtGui.QMouseEvent, 'globalPos'):
        QtGui.QMouseEvent.globalPos = lambda self: self.globalPosition().toPoint()

    # QDropEvent compat
    if not hasattr(QtGui.QDropEvent, 'pos'):
        QtGui.QDropEvent.pos = lambda self: self.position().toPoint()
    if not hasattr(QtGui.QDropEvent, 'keyboardModifiers'):
        QtGui.QDropEvent.keyboardModifiers = lambda self: self.modifiers()

    # QModelIndex.child() removed in Qt6
    if not hasattr(QtCore.QModelIndex, 'child'):
        def _qmodelindex_child(self, row, column=0):
            m = self.model()
            return m.index(row, column, self) if m else QtCore.QModelIndex()
        QtCore.QModelIndex.child = _qmodelindex_child
    if not hasattr(QtCore.QPersistentModelIndex, 'child'):
        def _qpersistentmodelindex_child(self, row, column=0):
            m = self.model()
            return m.index(row, column, QtCore.QModelIndex(self)) if m else QtCore.QModelIndex()
        QtCore.QPersistentModelIndex.child = _qpersistentmodelindex_child

    # QPoint + QPointF: Qt6 is strict about mixing them
    _origQPointAdd = QtCore.QPoint.__add__
    def _qpoint_add(self, other):
        if isinstance(other, QtCore.QPointF):
            return QtCore.QPointF(self) + other
        return _origQPointAdd(self, other)
    QtCore.QPoint.__add__ = _qpoint_add

    # QPolygonF: accept QPoint in lists
    _OrigQPolygonF = QtGui.QPolygonF
    class _CompatQPolygonF(_OrigQPolygonF):
        def __init__(self, *args):
            if args and isinstance(args[0], list):
                super().__init__([QtCore.QPointF(p) if isinstance(p, QtCore.QPoint)
                                  else p for p in args[0]])
            else:
                super().__init__(*args)
    QtGui.QPolygonF = _CompatQPolygonF

    # Scoped enum promotion (PyQt5 compat)
    # Restores flat access: Qt.Key_V, QFrame.HLine, etc.
    def _promote_enums(cls):
        for attr_name in dir(cls):
            if attr_name.startswith('_'):
                continue
            obj = getattr(cls, attr_name, None)
            if obj is not None and hasattr(obj, '__members__'):
                for name, val in obj.__members__.items():
                    if not hasattr(cls, name):
                        try:
                            setattr(cls, name, val)
                        except (AttributeError, TypeError):
                            pass

    for _mod in (QtCore, QtGui, QtWidgets):
        for _name in dir(_mod):
            _cls = getattr(_mod, _name)
            if isinstance(_cls, type):
                _promote_enums(_cls)
    del _promote_enums, _mod, _name, _cls

    # QStandardPaths.DataLocation renamed
    if not hasattr(QtCore.QStandardPaths, 'DataLocation'):
        QtCore.QStandardPaths.DataLocation = QtCore.QStandardPaths.AppDataLocation

    LOGGER.debug("PyQt6 compatibility patches applied")

else:
    QAction = QtWidgets.QAction


###############################################################################
#  QScreen helpers (replaces deprecated QDesktopWidget)
###############################################################################
def screenAt(widget):
    """Return the QScreen for the given widget, or the primary screen."""
    if hasattr(QtWidgets.QApplication, 'screenAt'):
        pos = widget.mapToGlobal(widget.rect().center())
        screen = QtWidgets.QApplication.screenAt(pos)
        if screen:
            return screen
    return QtWidgets.QApplication.primaryScreen()


def screenNumber(widget):
    """Return the index of the screen containing *widget*."""
    screen = screenAt(widget)
    screens = QtWidgets.QApplication.screens()
    return screens.index(screen) if screen in screens else 0


def screenGeometry(index):
    """Return the QRect geometry of screen *index*."""
    screens = QtWidgets.QApplication.screens()
    if 0 <= index < len(screens):
        return screens[index].geometry()
    primary = QtWidgets.QApplication.primaryScreen()
    return primary.geometry() if primary else QtCore.QRect()


###############################################################################
#  QRegExp wrapper (QRegExp removed in Qt6)
###############################################################################
if QT_VERSION == 6:
    _QRegularExpression = QtCore.QRegularExpression

    class QRegExp:
        """Minimal QRegExp-like wrapper around QRegularExpression for Qt6."""

        def __init__(self, pattern=""):
            self._pattern = pattern
            self._options = _QRegularExpression.PatternOption.NoPatternOption
            self._re = _QRegularExpression(pattern, self._options)
            self._lastMatch = None

        def setPattern(self, pattern):
            self._pattern = pattern
            self._re.setPattern(pattern)

        def pattern(self):
            return self._pattern

        def setCaseSensitivity(self, cs):
            if cs == 0:  # Qt.CaseInsensitive
                self._options = _QRegularExpression.PatternOption.CaseInsensitiveOption
            else:
                self._options = _QRegularExpression.PatternOption.NoPatternOption
            self._re.setPatternOptions(self._options)

        def setMinimal(self, minimal):
            if minimal:
                opts = self._re.patternOptions()
                self._re.setPatternOptions(
                    opts | _QRegularExpression.PatternOption.InvertedGreedinessOption)

        def indexIn(self, text, offset=0):
            self._lastMatch = self._re.match(text, offset)
            return self._lastMatch.capturedStart() if self._lastMatch.hasMatch() else -1

        def exactMatch(self, text):
            m = self._re.match(text)
            return m.hasMatch() and m.capturedLength() == len(text)

        def cap(self, n=0):
            if self._lastMatch and self._lastMatch.hasMatch():
                return self._lastMatch.captured(n)
            return ""

        def pos(self, n=0):
            if self._lastMatch and self._lastMatch.hasMatch():
                return self._lastMatch.capturedStart(n)
            return -1

        def matchedLength(self):
            if self._lastMatch and self._lastMatch.hasMatch():
                return self._lastMatch.capturedLength()
            return -1

        def captureCount(self):
            return self._re.captureCount()

        def capturedTexts(self):
            if self._lastMatch and self._lastMatch.hasMatch():
                return [self._lastMatch.captured(i)
                        for i in range(self._lastMatch.lastCapturedIndex() + 1)]
            return []

else:
    QRegExp = QtCore.QRegExp


###############################################################################
#  Wayland platform defaults
###############################################################################
def applyWaylandDefaults():
    """Configure the platform for native Wayland rendering.

    Must be called BEFORE QApplication is created.
    """
    # Use native Wayland rendering.
    if 'QT_QPA_PLATFORM' not in os.environ:
        if os.environ.get('XDG_SESSION_TYPE') == 'wayland':
            os.environ['QT_QPA_PLATFORM'] = 'wayland'

    # Let the compositor handle window decorations.
    os.environ.setdefault('QT_WAYLAND_DISABLE_WINDOWDECORATION', '1')

    if QT_VERSION == 6:
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts, True)
    else:
        try:
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts, True)
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            pass
