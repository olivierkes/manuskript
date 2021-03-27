from ..enums import Character as C


class SpellcheckNames:
    """
    An interface responsible for watching for changes in
    the character model, and updating the spellchecking 
    dictionary accordingly.

    This could probably be expanded in the future to also
    track other proper names, such as place names.
    """

    def __init__(self, onChangedCallback):
        self.mdlCharacter = None
        self.dictionary = None
        self.characterNames = set()
        self.onChangedCallback = onChangedCallback
    

    def onDictionaryChanged(self, newDictionary):
        """
        Adds the names of all characters to the new dictionary

        Call this once when spellcheking is first initialized, 
        and afterward any time the spellchecking dictionary is 
        changed.
        """
        self.dictionary = newDictionary
        if self.dictionary is not None:
            self.dictionary.addWords(self.characterNames)
    

    def onCharacterModelChanged(self, newModel):
        """
        Updates the spellchecking dictionary with the changes
        to names in the character model.

        Call this to pass an entirely new 
        character should that need ever arise.
        """
        self.mdlCharacter = newModel
        self._updateAll()
    

    def _updateAll(self):
        if self.mdlCharacter is None:
            # No character model has been initialized yet
            return
        # Get the differences between the current and previous names
        currentNames = set(name 
            for character in self.mdlCharacter.characters
            for name in character.name().split()) # Add given names and surname seperately
        addedNames = currentNames - self.characterNames
        removedNames = self.characterNames - currentNames
        self.characterNames = currentNames
        # Actually update the dictionary
        if self.dictionary is not None and (addedNames or removedNames):
            self.dictionary.removeWords(removedNames)
            self.dictionary.addWords(addedNames)
            self.onChangedCallback()
    

    def onCharacterModelUpdated(self, index):
        """
        Updates the spellchecking dictionary with the changes
        to names in the character model.

        Call this when any changes have been made to character 
        names.
        """
        if index.column() != C.name:
            # Only update the dictionary if the name has changed, not anything 
            # else about the character
            return
        # There's not really a good way to get the original value of the name,
        # so we still just call updateAll.
        self._updateAll()




