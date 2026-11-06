"""Tests for the character reference sidebar."""

from manuskript.ui.characterCard import CharacterCard


def test_character_pinning(MWEmptyProject):
    """Characters can be pinned, unpinned, and cleared."""

    mw = MWEmptyProject

    # Create two characters
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    bob = mw.mdlCharacter.addCharacter(name="Bob")

    # Initially, neither character is pinned
    assert mw.pinnedCharacterIDs == []

    # Pin Alice
    mw.toggleCharacterPin(alice)

    assert mw.pinnedCharacterIDs == [alice.ID()]

    # Pin Bob
    mw.toggleCharacterPin(bob)

    assert mw.pinnedCharacterIDs == [
        alice.ID(),
        bob.ID()
    ]

    # Unpin Alice
    mw.toggleCharacterPin(alice)

    assert mw.pinnedCharacterIDs == [bob.ID()]

    # Clear all pins
    mw.clearCharacterPins()

    assert mw.pinnedCharacterIDs == []

def test_character_creation(MWEmptyProject):
    """Creating characters should not cause shutdown errors."""

    mw = MWEmptyProject

    alice = mw.mdlCharacter.addCharacter(name="Alice")
    bob = mw.mdlCharacter.addCharacter(name="Bob")

    assert alice.name() == "Alice"
    assert bob.name() == "Bob"

def test_character_pin_only(MWEmptyProject):
    """Pinning one character should exit cleanly."""

    mw = MWEmptyProject
    alice = mw.mdlCharacter.addCharacter(name="Alice")

    mw.toggleCharacterPin(alice)

    assert mw.pinnedCharacterIDs == [alice.ID()]

def test_character_pin_unpin(MWEmptyProject):
    """Pinning and unpinning should exit cleanly."""

    mw = MWEmptyProject
    alice = mw.mdlCharacter.addCharacter(name="Alice")

    mw.toggleCharacterPin(alice)
    assert mw.pinnedCharacterIDs == [alice.ID()]

    mw.toggleCharacterPin(alice)
    assert mw.pinnedCharacterIDs == []

def test_character_clear_pins(MWEmptyProject):
    """Clearing multiple pinned characters should exit cleanly."""

    mw = MWEmptyProject

    alice = mw.mdlCharacter.addCharacter(name="Alice")
    bob = mw.mdlCharacter.addCharacter(name="Bob")

    mw.toggleCharacterPin(alice)
    mw.toggleCharacterPin(bob)

    assert mw.pinnedCharacterIDs == [
        alice.ID(),
        bob.ID()
    ]

    mw.clearCharacterPins()

    assert mw.pinnedCharacterIDs == []

def test_deleting_pinned_character(MWEmptyProject):
    """Deleting a character removes it from the pinned list."""

    mw = MWEmptyProject

    alice = mw.mdlCharacter.addCharacter(name="Alice")
    bob = mw.mdlCharacter.addCharacter(name="Bob")

    mw.toggleCharacterPin(alice)
    mw.toggleCharacterPin(bob)

    assert mw.pinnedCharacterIDs == [
        alice.ID(),
        bob.ID()
    ]

    # Delete Alice through the character model.
    alice_id = alice.ID()
    bob_id = bob.ID()

    mw.mdlCharacter.removeCharacter(alice_id)

    assert alice_id not in [
        character.ID()
        for character in mw.mdlCharacter.characters
    ]

    assert alice_id not in mw.pinnedCharacterIDs
    assert mw.pinnedCharacterIDs == [bob_id]

def test_character_search(MWEmptyProject):
    """Searching filters character cards without changing character data."""

    mw = MWEmptyProject

    mw.mdlCharacter.addCharacter(name="Alice")
    mw.mdlCharacter.addCharacter(name="Bob")
    mw.mdlCharacter.addCharacter(name="Charlotte")

    def visible_characters():
        """Return the names of characters currently shown in the sidebar."""

        names = []

        for i in range(mw.characterCardLayout.count()):
            widget = mw.characterCardLayout.itemAt(i).widget()

            if isinstance(widget, CharacterCard):
                names.append(widget.character.name())

        return names

    # Initially, all characters appear.
    assert visible_characters() == [
        "Alice",
        "Bob",
        "Charlotte"
    ]

    # Search is case-insensitive.
    mw.characterSearch.setText("ALICE")

    assert visible_characters() == ["Alice"]

    # Partial names work.
    mw.characterSearch.setText("arl")

    assert visible_characters() == ["Charlotte"]

    # Nonmatching searches display no characters.
    mw.characterSearch.setText("Nobody")

    assert visible_characters() == []

    # Clearing the search restores all characters.
    mw.characterSearch.clear()

    assert visible_characters() == [
        "Alice",
        "Bob",
        "Charlotte"
    ]

    # Searching doesn't remove characters from the model.
    assert len(mw.mdlCharacter.characters) == 3

def test_character_pins_persist(MWNoProject, tmp_path):
    """Pinned characters survive saving and reopening a project."""

    mw = MWNoProject

    project = tmp_path / "character-pins.msk"

    # Create a fresh project.
    mw.welcome.createFile(str(project), overwrite=True)

    assert mw.currentProject is not None

    # Create two characters.
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    bob = mw.mdlCharacter.addCharacter(name="Bob")

    alice_id = alice.ID()
    bob_id = bob.ID()

    # Pin Bob first to verify that pin order is preserved.
    mw.toggleCharacterPin(bob)
    mw.toggleCharacterPin(alice)

    assert mw.pinnedCharacterIDs == [bob_id, alice_id]

    # Save the project.
    mw.saveDatas()

    assert mw.projectDirty is False
    assert project.exists()

    # Close and reopen.
    mw.closeProject()
    mw.loadProject(str(project))

    # Verify that the characters were restored.
    character_ids = [
        character.ID()
        for character in mw.mdlCharacter.characters
    ]

    assert alice_id in character_ids
    assert bob_id in character_ids

    # Verify that pins survived in the correct order.
    assert mw.pinnedCharacterIDs == [bob_id, alice_id]

def test_character_portrait_persists(MWNoProject, tmp_path):
    """Character portraits survive saving and reopening a project."""

    import base64

    mw = MWNoProject
    project = tmp_path / "character-portrait.msk"

    # Create a fresh project.
    mw.welcome.createFile(str(project), overwrite=True)

    # A tiny, valid PNG image.
    image_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwC"
        "AAAAC0lEQVR42mP8/x8AAwMCAO+/lXcAAAAASUVORK5CYII="
    )

    # Create a character and assign a portrait.
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    alice_id = alice.ID()

    alice.portraitPath = "alice.png"
    alice.portraitData = image_data

    # Save the project.
    mw.saveDatas()

    assert mw.projectDirty is False
    assert project.exists()

    # Verify that the image was saved inside the project folder.
    portrait_file = f"images/characters/{alice_id}.png"

    portrait_on_disk = (
        project.with_suffix("") / portrait_file
    )

    assert portrait_on_disk.exists()
    assert portrait_on_disk.read_bytes() == image_data

    # Close and reopen the project.
    mw.closeProject()
    mw.loadProject(str(project))

    # Find Alice in the reloaded character model.
    restored = next(
        character
        for character in mw.mdlCharacter.characters
        if character.ID() == alice_id
    )

    # Verify that her portrait was restored.
    assert restored.portraitData == image_data
    assert restored.portraitPath == portrait_file
#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Fixtures."""

import pytest

@pytest.fixture
def MW():
    """
    Returns the mainWindow
    """
    from manuskript import functions as F
    MW = F.mainWindow()
    assert MW != None
    assert MW == F.MW

    return MW

@pytest.fixture
def MWNoProject(MW):
    """
    Take the MainWindow and close andy possibly open project.
    """
    MW.closeProject()
    assert MW.currentProject == None
    return MW

@pytest.fixture
def MWEmptyProject(MW):
    """
    Creates a MainWindow and load an empty project.
    """
    import tempfile
    tf = tempfile.NamedTemporaryFile(suffix=".msk")

    MW.closeProject()
    assert MW.currentProject == None
    MW.welcome.createFile(tf.name, overwrite=True)
    assert MW.currentProject != None
    return MW

    # If using with: @pytest.fixture(scope='session', autouse=True)
    # yield MW
    # # Properly destructed after. Otherwise: seg fault.
    # MW.deleteLater()

@pytest.fixture
def MWSampleProject(MW):
    """
    Creates a MainWindow and load a copy of the Acts sample project.
    """

    from manuskript import functions as F
    import os
    # Get the path of the first sample project. We assume it is here.
    spDir = F.appPath("sample-projects")
    lst = os.listdir(spDir)
    # We assume it's saved in folder, so there is a `name.msk` file and a
    # `name` folder.
    src = [f for f in lst if f[-4:] == ".msk" and f[:-4] in lst][0]
    src = os.path.join(spDir, src)
    # Copy to a temp file
    import tempfile
    tf = tempfile.NamedTemporaryFile(suffix=".msk")
    import shutil
    shutil.copyfile(src, tf.name)
    shutil.copytree(src[:-4], tf.name[:-4])
    MW.loadProject(tf.name)
    assert MW.currentProject != None

    return MW

# Append these helpers and eight tests to manuskript/tests/ui/test_characterSidebar.py.


def _sidebar_cards(mw):
    """Current cards in display order (excluding headings)."""
    from manuskript.ui.characterCard import CharacterCard

    return [
        mw.characterCardLayout.itemAt(i).widget()
        for i in range(mw.characterCardLayout.count())
        if isinstance(mw.characterCardLayout.itemAt(i).widget(), CharacterCard)
    ]


def _test_image_bytes(fmt="PNG"):
    """Generate a valid tiny image without external test fixtures."""
    from PyQt5.QtCore import QBuffer, QByteArray, QIODevice
    from PyQt5.QtGui import QImage, QColor

    image = QImage(3, 3, QImage.Format_RGB32)
    image.fill(QColor("red"))
    output = QByteArray()
    buffer = QBuffer(output)
    assert buffer.open(QIODevice.WriteOnly)
    assert image.save(buffer, fmt)
    buffer.close()
    return bytes(output)


def test_character_portrait_zip_persists(MWNoProject, tmp_path, monkeypatch):
    """ZIP projects embed portraits and restore them on reopening."""
    import zipfile
    from manuskript import settings

    mw = MWNoProject
    project = tmp_path / "portrait-zip.msk"
    mw.welcome.createFile(str(project), overwrite=True)
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    alice_id = alice.ID()
    image_data = _test_image_bytes()
    alice.portraitPath = "alice.png"
    alice.portraitData = image_data

    monkeypatch.setattr(settings, "saveToZip", True)
    mw.saveDatas()
    assert mw.projectDirty is False
    assert zipfile.is_zipfile(project)
    portrait_file = f"images/characters/{alice_id}.png"
    with zipfile.ZipFile(project) as archive:
        assert archive.read(portrait_file) == image_data

    mw.closeProject()
    mw.loadProject(str(project))
    restored = mw.mdlCharacter.getCharacterByID(alice_id)
    assert restored is not None
    assert restored.portraitPath == portrait_file
    assert restored.portraitData == image_data


def test_replacing_character_portrait_removes_old_file(MWNoProject, tmp_path, monkeypatch):
    """Replacing PNG with JPEG removes the obsolete file in folder projects."""
    from manuskript import settings

    mw = MWNoProject
    project = tmp_path / "replace-portrait.msk"
    mw.welcome.createFile(str(project), overwrite=True)
    monkeypatch.setattr(settings, "saveToZip", False)
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    folder = project.with_suffix("") / "images" / "characters"
    png_path = folder / f"{alice.ID()}.png"
    jpeg_path = folder / f"{alice.ID()}.jpeg"

    alice.portraitPath = "alice.png"
    alice.portraitData = _test_image_bytes("PNG")
    mw.saveDatas()
    assert png_path.read_bytes() == alice.portraitData

    jpeg_bytes = _test_image_bytes("JPEG")
    alice.portraitPath = "alice.jpeg"
    alice.portraitData = jpeg_bytes
    mw.saveDatas()
    assert not png_path.exists()
    assert jpeg_path.read_bytes() == jpeg_bytes


def test_deleting_character_removes_portrait(MWNoProject, tmp_path, monkeypatch):
    """Deleting a character removes its saved portrait on the next save."""
    from manuskript import settings

    mw = MWNoProject
    project = tmp_path / "delete-portrait.msk"
    mw.welcome.createFile(str(project), overwrite=True)
    monkeypatch.setattr(settings, "saveToZip", False)
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    alice_id = alice.ID()
    alice.portraitPath = "alice.png"
    alice.portraitData = _test_image_bytes()
    mw.saveDatas()
    portrait = project.with_suffix("") / "images" / "characters" / f"{alice_id}.png"
    assert portrait.exists()

    mw.mdlCharacter.removeCharacter(alice_id)
    mw.saveDatas()
    assert not portrait.exists()


def test_switching_projects_resets_sidebar(MWNoProject, tmp_path):
    """Pins and search text do not leak into another project."""
    mw = MWNoProject
    first = tmp_path / "first.msk"
    second = tmp_path / "second.msk"
    mw.welcome.createFile(str(first), overwrite=True)
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    mw.toggleCharacterPin(alice)
    mw.characterSearch.setText("ali")
    mw.saveDatas()
    mw.closeProject()

    mw.welcome.createFile(str(second), overwrite=True)
    assert mw.pinnedCharacterIDs == []
    assert mw.characterSearch.text() == ""
    assert _sidebar_cards(mw) == []
    mw.saveDatas()
    mw.closeProject()

    mw.loadProject(str(first))
    assert mw.pinnedCharacterIDs == [alice.ID()]
    assert mw.characterSearch.text() == ""
    assert [card.character.name() for card in _sidebar_cards(mw)] == ["Alice"]


def test_pinned_cards_display_first_in_pin_order(MWEmptyProject):
    """Pinned cards precede unpinned cards, ordered by when they were pinned."""
    mw = MWEmptyProject
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    bob = mw.mdlCharacter.addCharacter(name="Bob")
    charlotte = mw.mdlCharacter.addCharacter(name="Charlotte")
    mw.toggleCharacterPin(charlotte)
    mw.toggleCharacterPin(bob)

    cards = _sidebar_cards(mw)
    assert [card.character.name() for card in cards] == ["Charlotte", "Bob", "Alice"]
    assert [card.pinButton.isChecked() for card in cards] == [True, True, False]
    assert [card.pinButton.text() for card in cards] == ["Unpin", "Unpin", "Pin"]


def test_sidebar_portrait_click_opens_character(MWEmptyProject):
    """Clicking a card portrait selects that character in the Characters tab."""
    mw = MWEmptyProject
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    bob = mw.mdlCharacter.addCharacter(name="Bob")
    card = next(card for card in _sidebar_cards(mw) if card.character.ID() == bob.ID())

    # Exercise the clickable label's signal path without screen coordinates.
    card.portraitLabel.clicked.emit()
    assert mw.tabMain.currentIndex() == mw.TabPersos
    assert mw.lstCharacters.currentCharacterID() == bob.ID()
    assert mw.lstCharacters.currentCharacterID() != alice.ID()


def test_character_portrait_previews(MWEmptyProject):
    """A valid portrait renders in both the sidebar card and character editor."""
    mw = MWEmptyProject
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    alice.portraitPath = "alice.png"
    alice.portraitData = _test_image_bytes()
    mw.refreshCharacterSidebar()

    card = next(card for card in _sidebar_cards(mw) if card.character.ID() == alice.ID())
    assert card.portraitLabel.pixmap() is not None
    assert not card.portraitLabel.pixmap().isNull()

    mw.changeCurrentCharacter(alice)
    assert mw.lblPersoPortrait.pixmap() is not None
    assert not mw.lblPersoPortrait.pixmap().isNull()


def test_character_changes_mark_project_dirty(MWEmptyProject):
    """Pinning and clearing pins mark the project dirty; saving clears the flag."""
    mw = MWEmptyProject
    alice = mw.mdlCharacter.addCharacter(name="Alice")
    mw.saveDatas()
    assert mw.projectDirty is False

    mw.toggleCharacterPin(alice)
    assert mw.projectDirty is True
    mw.saveDatas()
    assert mw.projectDirty is False

    mw.clearCharacterPins()
    assert mw.projectDirty is True
    mw.saveDatas()
    assert mw.projectDirty is False

    # The portrait chooser also calls startTimerNoChanges after selecting an image.
    # Exercise that method through a mocked file picker, without a modal dialog.
    from unittest.mock import patch
    from PyQt5.QtGui import QImage, QColor
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as directory:
        image_path = os.path.join(directory, "portrait.png")
        image = QImage(3, 3, QImage.Format_RGB32)
        image.fill(QColor("blue"))
        assert image.save(image_path)
        item = mw.lstCharacters.getItemByID(alice.ID())
        assert item is not None
        mw.lstCharacters.setCurrentItem(item)
        with patch("manuskript.mainWindow.QFileDialog.getOpenFileName", return_value=(image_path, "")):
            mw.chooseCharacterPortrait()
        assert mw.projectDirty is True
        assert alice.portraitData == open(image_path, "rb").read()
