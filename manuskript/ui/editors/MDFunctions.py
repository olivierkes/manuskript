#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QTextCursor


def MDFormatSelection(editor, style):
    """
    Formats the current selection of ``editor`` in the format given by ``style``, 
    style being:
        0: bold
        1: italic
        2: code
    """
    print("Formatting:", style, " (Unimplemented yet !)")
    # FIXME