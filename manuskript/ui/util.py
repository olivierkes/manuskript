#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi

gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, Gdk

from manuskript.data import Color, OutlineItem, OutlineText, OutlineFolder


def rgbaFromColor(color: Color) -> Gdk.RGBA:
    rgba = Gdk.RGBA()
    rgba.red = 0 if color is None else color.red / 255.
    rgba.green = 0 if color is None else color.green / 255.
    rgba.blue = 0 if color is None else color.blue / 255.
    rgba.alpha = 1.
    return rgba


def pixbufFromColor(color: Color) -> GdkPixbuf:
    pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 16, 16)
    pixbuf.fill(0 if color is None else color.getRGB())
    return pixbuf


def bindMenuItem(builder, id, action):
    menuItem = builder.get_object(id)

    if menuItem is None:
        return

    menuItem.connect("activate", action)


def iconByOutlineItemType(outlineItem: OutlineItem) -> str:
    if type(outlineItem) is OutlineFolder:
        return "folder-symbolic"
    elif type(outlineItem) is OutlineText:
        return "emblem-documents-symbolic"
    else:
        return "folder-documents-symbolic"
