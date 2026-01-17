#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import pypandoc
except ModuleNotFoundError:
    pypandoc = None

from manuskript.converter.abstractConverter import AbstractConverter


class PandocConverter(AbstractConverter):

    def __init__(self):
        AbstractConverter.__init__(self)

        if pypandoc is None:
            inputFormats = []
            outputFormats = []
        else:
            inputFormats, outputFormats = pypandoc.get_pandoc_formats()

        for inputFormat in inputFormats:
            self.inputFormats.append(inputFormat)
        
        for outputFormat in outputFormats:
            self.outputFormats.append(outputFormat)
    
    def isValid(self) -> bool:
        return False if pypandoc is None else True

    def convert(self, text: str, inputFormat: str, outputFormat: str) -> str | None:
        if (self.supportsInput(inputFormat)) and (self.supportsOutput(outputFormat)):
            return pypandoc.convert_text(text, outputFormat, format=inputFormat)
        else:
            return AbstractConverter.convert(text, inputFormat, outputFormat)

    def convertFile(self, path: str, outputPath: str, inputFormat: str, outputFormat: str) -> bool:
        if (self.supportsInput(inputFormat)) and (self.supportsOutput(outputFormat)):
            try:
                pypandoc.convert_file(path, outputFormat, format=inputFormat, outputfile=outputPath)
                return True
            except RuntimeError:
                return False
        else:
            return AbstractConverter.convert(text, inputFormat, outputFormat)
