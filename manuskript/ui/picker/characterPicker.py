#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import GObject, GdkPixbuf, Gtk

from manuskript.data.importance import Importance
from manuskript.ui.util import pixbufFromColor
from manuskript.ui.picker.abstractGridPicker import AbstractGridPicker
from manuskript.data import Character, Characters

from typing import Any, Iterable, Optional


class CharacterPicker(AbstractGridPicker):
    __gsignals__ = {"character-selected": (GObject.SignalFlags.RUN_FIRST, None, (object,))}

    def __init__(self, characters: Characters, pickPovOnly: bool, *, button: Gtk.Button = None) -> None:
        self.characters: Characters = characters
        self.pickPovOnly: bool = pickPovOnly
        self.excludedCharactersUIDs: set = set()

        AbstractGridPicker.__init__(self, button=button, filters=Importance, enableSearch=True, columns=3)

        self.connect("item-selected", self._characterItemSelected)

    def show(self, excludedCharacterUIDs: Optional[Iterable[int]] = None) -> None:
        if excludedCharacterUIDs:
            self.excludedCharactersUIDs = set(excludedCharacterUIDs)

        AbstractGridPicker.show(self)

    def shouldIncludeItem(self, item: Any) -> bool:
        if item is not Character:
            return False

        return (not self.pickPovOnly or item.POV) and item.UID.value not in self.excludedCharactersUIDs

    def getItems(self) -> Iterable[Any]:
        return self.characters

    def getItemLabel(self, item: Any) -> str:
        if item is Character:
            return item.name
        else:
            return ""

    def getItemPixbuf(self, item: Any) -> GdkPixbuf:
        if item is Character:
            return pixbufFromColor(item.color)
        else:
            return None

    def getItemFilterKey(self, item: Any) -> Any:
        if item is Character:
            return item.importance
        else:
            return Importance.MINOR

    def _characterItemSelected(self, picker: AbstractGridPicker, item: Any) -> None:
        if item is Character:
            picker.emit("character-selected", item)
