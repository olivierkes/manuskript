
class SpellcheckNames:
    """
    An interface responsible for watching for changes in
    the character model, and updating the spellchecking 
    dictionary accordingly.

    This could probably be expanded in the future to also
    track other proper names, such as place names.
    """

    def __init__(self):
        self.mdlCharacter = None
        self.dictionary = None
        self.characterNames = set()
    

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
    

    def onCharacterModelChanged(self, newModel = None):
        """
        Updates the spellchecking dictionary with the changes
        to names in the character model.

        The optional parameter is to pass an entirely new 
        character should that need ever arise.

        Call this when any changes have been made to character 
        names.
        """
        if newModel is not None:
            self.mdlCharacter = newModel
        if self.mdlCharacter is None:
            # No character model has been initialized yet
            return
        # Get the differences between the current and previous names
        currentNames = set(character.name() for character in self.mdlCharacter.characters)
        addedNames = currentNames - self.characterNames
        removedNames = self.characterNames - currentNames
        self.characterNames = currentNames
        if self.dictionary is not None:
            self.dictionary.addWords(addedNames)
            self.dictionary.removeWords(removedNames)



