#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.converter.abstractConverter import AbstractConverter


__converters__ = []


def getConverters() -> list:
    global __converters__
    return filter(lambda converter: converter.isValid(), __converters__)


def getConverter(inputFormat: str, outputFormat: str) -> AbstractConverter | None:
    for converter in getConverters():
        if (converter.supportsInput(inputFormat)) and (converter.supportsOutput(outputFormat)):
            return converter
    
    return None


def registerConverter(converter: AbstractConverter) -> bool:
    global __converters__

    if not converter.isValid():
        return False
    
    if converter in __converters__:
        return False
    
    __converters__.append(converter)
    return True


def unregisterConverter(converter: AbstractConverter) -> bool:
    global __converters__

    if not converter in __converters__:
        return False
    
    __converters__.remove(converter)
    return True
