#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for outlineItem"""

import pytest


@pytest.fixture
def outlineItemFolder():
    '''Returns a folder outlineItem title "Folder".'''
    from manuskript.models import outlineItem
    return outlineItem(title="Folder")

@pytest.fixture
def outlineItemText():
    '''Returns a text outlineItem title "Text".'''
    from manuskript.models import outlineItem
    return outlineItem(title="Text", _type="md")

def test_outlineItemsProperties(outlineItemFolder, outlineItemText):
    """
    Tests with simple items, without parent or models.
    """

    from PyQt5.QtCore import Qt

    # Simplification
    folder = outlineItemFolder
    text = outlineItemText

    # getters
    assert folder.isFolder() == True
    assert text.isFolder() == False
    assert text.isText() == True
    assert text.isMD() == text.isMMD() == True
    assert text.title() == "Text"
    assert text.compile() == True
    assert folder.POV() == ""
    assert folder.status() == ""
    assert folder.label() == ""
    assert folder.customIcon() == ""
    assert folder.data(42) == ""
    assert folder.data(folder.enum.title, role=Qt.CheckStateRole) == None

    # setData and other setters
    assert text.data(text.enum.compile, role=Qt.CheckStateRole) == Qt.Checked
    text.setData(text.enum.compile, 0)
    assert text.compile() == False
    assert text.data(text.enum.compile, role=Qt.CheckStateRole) == Qt.Unchecked
    folder.setCustomIcon("custom")
    assert folder.customIcon() == "custom"
    folder.setData(folder.enum.text, "Some text")
    assert folder.text() == ""  # folders have no text

    # wordCount
    text.setData(text.enum.text, "Sample **text**.")
    assert text.wordCount() == 2
    text.setData(text.enum.goal, 4)
    assert text.data(text.enum.goalPercentage) == .5

    # revisions
    assert text.data(text.enum.revisions) == []

def test_modelStuff(outlineModelBasic):
    """
    Tests with children items.
    """

    # Simplification
    model = outlineModelBasic

    # Child count
    root = model.rootItem
    assert len(root.children()) == 2
    folder = root.child(0)
    text1 = folder.child(0)
    text2 = root.child(1)

    # Compile
    assert text1.compile() == True
    folder.setData(folder.enum.compile, 0)
    assert text1.compile() == False

    # Word count
    text1.setData(text1.enum.text, "Sample text.")
    assert text1.wordCount() == 2
    assert folder.wordCount() == 2
    statsWithGoal = folder.stats()
    assert statsWithGoal != ""
    text1.setData(text1.enum.setGoal, 4)
    assert folder.data(folder.enum.goal) == 4
    folder.setData(folder.enum.setGoal, 3)
    assert folder.data(folder.enum.goal) == 3
    assert folder.stats() != statsWithGoal

    # Split and merge
    text1.setData(text1.enum.text, "Sample\n---\ntext.")
    folder.split("invalid mark")
    assert folder.childCount() == 1
    folder.split("\n---\n")
    assert folder.childCount() == 2
    text1.mergeWith([folder.child(1)])
    assert text1.text() == "Sample\n\ntext."
    text1.setData(text1.enum.text, "Sample\nNewTitle\ntext.")
    text1.splitAt(7, 8)
    assert folder.child(1).title() == "NewTitle"
    folder.child(1).splitAt(3)
    assert folder.child(2).title() == "NewTitle_2"
    folder.removeChild(2)
    folder.removeChild(1)
    folder.removeChild(0)
    assert folder.childCount() == 0

    # Search
    folder.appendChild(text2)
    text2.setData(text2.enum.POV, 1)
    folder.setData(folder.enum.POV, 1)
    assert len(folder.findItemsByPOV(1)) == 2
    folder.setData(folder.enum.label, 1)  # Idea
    folder.setData(folder.enum.status, 4) # Final
    text2.setData(text2.enum.text, "Some final value.")
    from manuskript.functions import MW
    cols = [folder.enum.text, folder.enum.POV,
            folder.enum.label, folder.enum.status]
    assert folder.findItemsContaining("VALUE", cols,  MW, True) == []
    assert folder.findItemsContaining("VALUE", cols,  MW, False) == [text2.ID()]

    # Revisions
    text2.clearAllRevisions()
    assert text2.revisions() == []
    text2.setData(text2.enum.text, "Some value.")
    assert len(text2.revisions()) == 1
    text2.setData(text2.enum.text, "Some new value.")
    assert len(text2.revisions()) == 1  # Auto clean
    text2.deleteRevision(text2.revisions()[0][0])
    assert len(text2.revisions()) == 0

    # Model, count and copy
    k = folder._model
    folder.setModel(14)
    assert text2._model == 14
    folder.setModel(k)
    assert folder.columnCount() == len(folder.enum)
    text1 = text2.copy()
    assert text1.ID() is None
    folder.appendChild(text1)
    assert text1.ID() is not None
    assert folder.childCountRecursive() == 2
    assert text1.path() == "Folder > Text"
    assert len(text1.pathID()) == 2

    # IDs
    folder2 = folder.copy()
    text3 = text1.copy()
    text3.setData(text3.enum.ID, "0")
    folder2.appendChild(text3)
    folder.appendChild(folder2)
    assert text3.ID() == "0"
    root.checkIDs()
    assert text3.ID() != "0"
