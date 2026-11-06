#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from typing import Any, Callable, Type

from gi.repository import GdkPixbuf, Gdk, Gtk

from manuskript.data import Color, OutlineItem, OutlineText, OutlineFolder
from manuskript.util import getTranslation, profileTime


def rgbaFromColor(color: Color | None) -> Gdk.RGBA:
    rgba = Gdk.RGBA()
    rgba.red = 0 if color is None else color.red / 255.0
    rgba.green = 0 if color is None else color.green / 255.0
    rgba.blue = 0 if color is None else color.blue / 255.0
    rgba.alpha = 1.0
    return rgba


def pixbufFromColor(color: Color | None) -> GdkPixbuf:
    pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 16, 16)
    pixbuf.fill(0 if color is None else color.getRGB())
    return pixbuf


def bindMenuItem(builder: Gtk.Builder, id: str, action: Callable) -> None:
    menuItem = builder.get_object(id)

    if menuItem is None:
        return

    menuItem.connect("activate", action)


def packViewIntoSlot(slot: Gtk.Container, view_cls: Type, data: Any = None, secondaryData: Any = None):
    if slot is None:
        return None

    for child in slot.get_children():
        slot.remove(child)

    try:
        args = []
        if data is not None:
            args.append(data)
        if secondaryData is not None:
            args.append(secondaryData)

        view = profileTime(view_cls, *args)

    except Exception as e:
        print(str(e), file=sys.stderr)
        return None

    if view.widget is None:
        return None

    slot.pack_start(view.widget, True, True, 0)
    return view


def unpackFromSlot(slot: Gtk.Container, view) -> None:
    if (slot is not None) and (view.widget is not None):
        slot.remove(view.widget)

    del view


def iconByOutlineItemType(outlineItem: OutlineItem) -> str:
    if type(outlineItem) is OutlineFolder:
        return "folder-symbolic"
    elif type(outlineItem) is OutlineText:
        return "emblem-documents-symbolic"
    else:
        return "folder-documents-symbolic"
