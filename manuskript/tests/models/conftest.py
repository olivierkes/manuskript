#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Conf for models."""

import pytest

@pytest.fixture
def outlineModelBasic(MWEmptyProject):
    """Returns an outlineModel with a few items:
      * Folder
        * Text
      * Text
    """
    from manuskript.models import outlineItem
    mdl = MWEmptyProject.mdlOutline

    root = mdl.rootItem
    f = outlineItem(title="Folder", parent=root)
    t1 = outlineItem(title="Text", _type="md", parent=f)
    t2 = outlineItem(title="Text", _type="md", parent=root)

    return mdl
