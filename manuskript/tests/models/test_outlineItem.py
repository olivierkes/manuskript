#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for outlineItem"""

import pytest

from manuskript.models.outlineItem import outlineItem

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
