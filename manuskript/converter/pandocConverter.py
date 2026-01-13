#!/usr/bin/env python
# --!-- coding: utf8 --!--

import pypandoc

from manuskript.converter.abstractConverter import AbstractConverter


class PandocConverter(AbstractConverter):

    def __init__(self):
        AbstractConverter.__init__(self)

        inputFormats, outputFormats = pypandoc.get_pandoc_formats()

        for inputFormat in inputFormats:
            self.inputFormats.append(inputFormat)
        
        for outputFormat in outputFormats:
            self.outputFormats.append(outputFormat)

    def convert(self, text: str, inputFormat: str, outputFormat: str) -> str | None:
        if (self.supportsInput(inputFormat)) and (self.supportsOutput(outputFormat)):
            return pypandoc.convert_text(text, outputFormat, format=inputFormat)
        else:
            return AbstractConverter.convert(text, inputFormat, outputFormat)
