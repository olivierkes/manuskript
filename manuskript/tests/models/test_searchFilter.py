#!/usr/bin/env python
# --!-- coding: utf8 --!--

import pytest
from manuskript.models.searchFilter import searchFilter


def test_searchFilter_constructionOk():
    filter = searchFilter("label", True, [3])
    assert filter.label() == "label"
    assert filter.enabled() is True
    assert filter.modelColumns() == [3]


def test_searchFilter_constructionOkWithNoneModelColumn():
    filter = searchFilter("label", True)
    assert filter.label() == "label"
    assert filter.enabled() is True
    assert filter.modelColumns() == []


def test_searchFilter_constructionBadLabelType():
    with pytest.raises(TypeError, match=r".*label must be a str.*"):
        searchFilter(13, True, [3])


def test_searchFilter_constructionBadEnabledType():
    with pytest.raises(TypeError, match=r".*enabled must be a bool.*"):
        searchFilter("label", 3, [3])


def test_searchFilter_constructionBadModelColumnType():
    with pytest.raises(TypeError, match=r".*modelColumns must be a list or None.*"):
        searchFilter("label", False, True)


def test_searchFilter_setEnabled():
    filter = searchFilter("label", True, [3])
    assert filter.enabled() is True
    filter.setEnabled(False)
    assert filter.enabled() is False
