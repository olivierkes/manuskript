#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, Gdk

from manuskript.data import Color


def rgbaFromColor(color: Color) -> Gdk.RGBA:
    rgba = Gdk.RGBA()
    rgba.red = color.red / 255.
    rgba.green = color.green / 255.
    rgba.blue = color.blue / 255.
    rgba.alpha = 1.
    return rgba


def pixbufFromColor(color: Color) -> GdkPixbuf:
    if color is None:
        return None

    pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 16, 16)
    pixbuf.fill(color.getRGB())
    return pixbuf


def bindMenuItem(builder, id, action):
    menuItem = builder.get_object(id)

    if menuItem is None:
        return

    menuItem.connect("activate", action)
