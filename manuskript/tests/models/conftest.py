#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Conf for models."""

import pytest
from manuskript.models import outlineModel, outlineItem

@pytest.fixture
def outlineModelBasic(MWEmptyProject):
    """Returns an outlineModel with a few items:
      * Folder
        * Text
      * Text
    """
    mdl = MWEmptyProject.mdlOutline

    root = mdl.rootItem
    f = outlineItem(title="Folder", parent=root)
    t1 = outlineItem(title="Text 1", _type="md", parent=f)
    t2 = outlineItem(title="Text 2", _type="md", parent=root)

    return mdl
