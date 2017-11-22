#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""
The converters package provide functions to quickly convert on the fly from
one format to another. It is responsible to check what external library are
present, and do the job as best as possible with what we have in hand.
"""

from manuskript.converters.abstractConverter import abstractConverter
from manuskript.converters.pandocConverter import pandocConverter
#from manuskript.converters.markdownConverter import markdownConverter


def HTML2MD(html):

    # Convert using pandoc
    if pandocConverter.isValid():
        return pandocConverter.convert(html, _from="html", to="markdown")

    # Convert to plain text using QTextEdit
    return HTML2PlainText(html)


def HTML2PlainText(html):
    """
    Convert from HTML to plain text.
    """

    if pandocConverter.isValid():
        return pandocConverter.convert(html, _from="html", to="plain")

    # Last resort: probably resource ineficient
    e = QTextEdit()
    e.setHtml(html)
    return e.toPlainText()
