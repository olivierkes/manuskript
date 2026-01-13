#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.converter.abstractConverter import AbstractConverter
from manuskript.converter.markdownConverter import MarkdownConverter
from manuskript.converter.pandocConverter import PandocConverter


__converters__ = list(filter(lambda converter: converter.isValid(), [
    MarkdownConverter(),
    PandocConverter()
]))


def getConverters() -> list:
    global __converters__
    return __converters__


def getConverter(inputFormat: str, outputFormat: str) -> AbstractConverter | None:
    for converter in getConverters():
        if (converter.supportsInput(inputFormat)) and (converter.supportsOutput(outputFormat)):
            return converter
    
    return None
