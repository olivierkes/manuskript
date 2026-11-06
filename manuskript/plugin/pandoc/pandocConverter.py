#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import pypandoc
except ModuleNotFoundError:
    pypandoc = None

from typing import Optional

from manuskript.converter.abstractConverter import AbstractConverter


class PandocConverter(AbstractConverter):
    def __init__(self) -> None:
        AbstractConverter.__init__(self)
        self.runtimeErrors: list[RuntimeError] = []

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

    def getError(self) -> str | None:
        if len(self.runtimeErrors) > 0:
            return str(self.runtimeErrors[-1])
        else:
            return None

    def convert(self, text: str, inputFormat: str, outputFormat: str) -> str | None:
        if (pypandoc is not None) and (self.supportsInput(inputFormat)) and (self.supportsOutput(outputFormat)):
            result: str = pypandoc.convert_text(text, outputFormat, format=inputFormat)
            return result
        else:
            return AbstractConverter.convert(self, text, inputFormat, outputFormat)

    def convertFile(self, path: str, outputPath: str, inputFormat: str, outputFormat: str) -> bool:
        if (pypandoc is not None) and (self.supportsInput(inputFormat)) and (self.supportsOutput(outputFormat)):
            try:
                pypandoc.convert_file(path, outputFormat, format=inputFormat, outputfile=outputPath)
                return True
            except RuntimeError as e:
                self.runtimeErrors.append(e)
                return False
        else:
            return AbstractConverter.convertFile(self, path, outputPath, inputFormat, outputFormat)
