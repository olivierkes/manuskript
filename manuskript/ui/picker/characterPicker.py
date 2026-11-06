#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import GObject, GdkPixbuf, Gtk
from typing import Any, Iterable, Optional

from manuskript.data import Character, Characters, Importance
from manuskript.ui.util import pixbufFromColor
from manuskript.ui.picker.abstractGridPicker import AbstractGridPicker
from manuskript.util import validString


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
        if type(item) is not Character:
            return False
        elif item.UID is None:
            return False

        if (not self.pickPovOnly) or (item.POV):
            return item.UID.value not in self.excludedCharactersUIDs
        else:
            return False

    def getItems(self) -> Iterable[Any]:
        return self.characters

    def getItemLabel(self, item: Any) -> str:
        if type(item) is Character:
            return validString(item.name)
        else:
            return ""

    def getItemPixbuf(self, item: Any) -> GdkPixbuf:
        if type(item) is Character:
            return pixbufFromColor(item.color)
        else:
            return None

    def getItemFilterKey(self, item: Any) -> Any:
        if type(item) is Character:
            return item.importance
        else:
            return Importance.MINOR

    def _characterItemSelected(self, picker: AbstractGridPicker, item: Any) -> None:
        if type(item) is Character:
            picker.emit("character-selected", item)
