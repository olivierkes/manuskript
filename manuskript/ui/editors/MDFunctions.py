#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from manuskript.qt_compat import QRegExp
from PyQt6.QtGui import QTextCursor

import logging
LOGGER = logging.getLogger(__name__)

def MDFormatSelection(editor, style):
    """
    Formats the current selection of ``editor`` in the format given by ``style``, 
    style being:
        0: bold
        1: italic
        2: code
    """
    LOGGER.error("Formatting: %s (Not implemented!)", style)
    # FIXME