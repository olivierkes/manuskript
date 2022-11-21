#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Test ParseMMDFile function."""

from collections import OrderedDict
from manuskript.load_save.version_1 import parseMMDFile


BASE = "title:          TheExampleNovel\n"
BASE += "ID:             42\n"
BASE += "type:           folder\n"
TEXT = BASE + '\n'
TEXT_WITH_NONE_AT_START = "None:           hello\n" + TEXT
TEXT_WITH_NONE_AT_END = BASE + "None:           hello\n\n"
TEXT_WITH_HANGING_SPACE = BASE + "     "
CONTENT = "Once upon a time, there was a dog"
TEXT_WITH_CONTENT = TEXT + CONTENT


def test_empty_string():
    """An empty string given to parseMMDFile."""
    result = parseMMDFile("")
    assert result == ([], '')


def test_text():
    """A result as a list of tuples"""
    result = parseMMDFile(TEXT)
    assert result == ([
        ('title', 'TheExampleNovel'),
        ('ID', '42'),
        ('type', 'folder')
    ], '')


def test_text_asdict():
    """A result as an OrderedDict."""
    result = parseMMDFile(TEXT, True)
    assert result == (OrderedDict([
        ('title', 'TheExampleNovel'),
        ('ID', '42'),
        ('type', 'folder')]
    ), '')


def test_text_with_none_at_start():
    """If the description is None, replace with an empty string."""
    result = parseMMDFile(TEXT_WITH_NONE_AT_START)
    assert result == ([
        ('', 'hello'),
        ('title', 'TheExampleNovel'),
        ('ID', '42'),
        ('type', 'folder')
    ], '')


def test_text_wth_none_at_end():
    """If the last description is None, replace with an empty string."""
    result = parseMMDFile(TEXT_WITH_NONE_AT_END)
    assert result == ([
        ('title', 'TheExampleNovel'),
        ('ID', '42'),
        ('type', 'folder'),
        ('', 'hello')
    ], '')


def test_text_hanging_space():
    """Hanging space invalidates the line."""
    result = parseMMDFile(TEXT_WITH_HANGING_SPACE)
    assert result == ([
        ('title', 'TheExampleNovel'),
        ('ID', '42')
    ], '')


def test_text_with_content():
    """The scene has text."""
    result = parseMMDFile(TEXT_WITH_CONTENT)
    assert result[1] == CONTENT
