#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

realpath = os.path.realpath(__file__)

sys.path.insert(1, os.path.join(os.path.dirname(realpath), '..'))

from manuskript.ui import MainWindow

path = os.path.join(sys.path[1], "sample-projects/book-of-acts")

window = MainWindow(path + ".msk")
window.run()
