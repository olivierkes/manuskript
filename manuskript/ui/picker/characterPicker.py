from manuskript.data.importance import Importance
from manuskript.ui.util import pixbufFromColor
from manuskript.ui.picker.abstractGridPicker import AbstractGridPicker
from gi.repository import GObject

class CharacterPicker(AbstractGridPicker):
    __gsignals__ = {
        "character-selected": (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, characters, *, button=None):
        self.characters = characters
        self.excludedCharactersUIDs = set()

        super().__init__(button=button, filters=Importance, enableSearch=True, columns=3)

        self.connect("item-selected", self._characterItemSelected)

    def show(self, excludedCharacterUids=None):
        if excludedCharacterUids:
            self.excludedCharactersUIDs = set(excludedCharacterUids)
        
        super().show()

    def shouldIncludeItem(self, character):
        return character.UID.value not in self.excludedCharactersUIDs

    def getItems(self):
        return self.characters

    def getItemLabel(self, character):
        return character.name

    def getItemPixbuf(self, character):
        return pixbufFromColor(character.color)

    def getItemFilterKey(self, character):
        return character.importance

    def _characterItemSelected(self, picker, character):
        picker.emit("character-selected", character)