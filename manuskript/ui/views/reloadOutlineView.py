#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk

from manuskript.data.outline import OutlineItem
from manuskript.ui.views.abstractView import AbstractView


class ReloadOutlineView(AbstractView):
    def __init__(self, reloadOutlineViews: list[ReloadOutlineView]) -> None:
        AbstractView.__init__(self)
        reloadOutlineViews.append(self)

    def reloadOutlineData(self, outlineItem: OutlineItem) -> None:
        pass
