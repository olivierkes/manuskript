#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests."""

import pytest

# We need a qApplication to be running, or all the calls to qApp
# will throw a seg fault.
from PyQt5.QtWidgets import QApplication
app = QApplication([])
