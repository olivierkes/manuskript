#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for outlineItem"""

import pytest

from manuskript.models import outlineItem

@pytest.fixture
def outlineItemFolder():
    '''Returns a folder outlineItem title "Folder".'''
    return outlineItem(title="Folder")

@pytest.fixture
def outlineItemText():
    '''Returns a text outlineItem title "Text".'''
    return outlineItem(title="Text", _type="md")

def test_outlineItemsProperties(outlineItemFolder, outlineItemText):

    # Simplification
    folder = outlineItemFolder
    text = outlineItemText

    # Basic tests
    assert folder.isFolder() == True
    assert text.isFolder() == False
    assert text.isText() == True
    assert text.isMD() == text.isMMD() == True

    assert text.title() == "Text"
    assert text.compile() == True
    text.setData(text.enum.compile, 0)
    assert text.compile() == False
    assert folder.POV() == ""
    assert folder.status() == ""
    assert folder.POV() == ""
    assert folder.customIcon() == ""
    folder.setCustomIcon("custom")
    assert folder.customIcon() == "custom"

    text.setData(text.enum.text, "Sample **text**.")
    assert text.wordCount() == 2
    assert text.data(text.enum.revisions) == []
    text.setData(text.enum.setGoal, 4)
    assert text.data(text.enum.goalPercentage) == .5

def test_modelStuff(outlineModelBasic):

    # Simplification
    model = outlineModelBasic

    root = model.rootItem
    assert len(root.children()) == 2
    folder = root.child(0)
    text1 = folder.child(0)
    text2 = root.child(1)
    assert text1.compile() == True
    folder.setData(folder.enum.compile, 0)
    assert text1.compile() == False

    text1.setData(text1.enum.text, "Sample text.")
    assert text1.wordCount() == 2
    assert folder.wordCount() == 2
    assert folder.stats() != ""

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
    folder.removeChild(1)
    folder.removeChild(0)
    assert folder.childCount() == 0
