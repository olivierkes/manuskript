#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

print("blub")

realpath = os.path.realpath(__file__)

sys.path.insert(1, os.path.join(os.path.dirname(realpath), '..'))

print("real")

from manuskript.ui import MainWindow

print("Hi")

mw = MainWindow()
mw.run()
