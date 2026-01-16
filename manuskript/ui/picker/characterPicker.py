from manuskript.data.importance import Importance
from manuskript.ui.util import pixbufFromColor
from manuskript.ui.picker.abstractGridPicker import AbstractGridPicker
from manuskript.data import Character, Characters
from gi.repository import GObject, GdkPixbuf
from typing import Iterable, Optional

class CharacterPicker(AbstractGridPicker):
    __gsignals__ = {
        "character-selected": (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, characters: Characters, *, button=None):
        self.characters: Characters = characters
        self.excludedCharactersUIDs: set = set()

        super().__init__(button=button, filters=Importance, enableSearch=True, columns=3)

        self.connect("item-selected", self._characterItemSelected)

    def show(self, excludedCharacterUids: Optional[Iterable[int]]=None):
        if excludedCharacterUids:
            self.excludedCharactersUIDs = set(excludedCharacterUids)
        
        super().show()

    def shouldIncludeItem(self, character: Character) -> bool:
        return character.UID.value not in self.excludedCharactersUIDs

    def getItems(self) -> Characters:
        return self.characters

    def getItemLabel(self, character: Character) -> str:
        return character.name

    def getItemPixbuf(self, character: Character) -> GdkPixbuf:
        return pixbufFromColor(character.color)

    def getItemFilterKey(self, character) -> Importance:
        return character.importance

    def _characterItemSelected(self, picker, character):
        picker.emit("character-selected", character)