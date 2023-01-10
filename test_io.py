#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# I put this here because otherwise I couldn't run it.
# I also added some tests and had to modify this to get it to run -- ShadowOfHassen
import os
import sys

# gi
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

realpath = os.path.realpath(__file__)
LOGO_FILE = 'icons/Manuskript/manuskript.svg'
#sys.path.insert(1, os.path.join(os.path.dirname(realpath), '..'))

from manuskript.ui import MainWindow


window = MainWindow("sample-projects/book-of-acts" + ".msk")
# Let's make this a bit fancier
window.window.set_icon(GdkPixbuf.Pixbuf.new_from_file(LOGO_FILE))

window.run()
