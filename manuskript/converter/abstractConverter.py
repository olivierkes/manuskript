#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.io import BinaryFile, TextFile


class AbstractConverter:

    def __init__(self):
        self.inputFormats = []
        self.outputFormats = []

    def isValid(self) -> bool:
        return False

    def supportsInput(self, inputFormat: str) -> bool:
        if inputFormat == "*":
            return True

        return inputFormat in self.inputFormats

    def supportsOutput(self, outputFormat: str) -> bool:
        if outputFormat == "*":
            return True

        return outputFormat in self.outputFormats

    def convert(self, text: str, inputFormat: str, outputFormat: str) -> str | None:
        if inputFormat == outputFormat:
            return text
        else:
            return None

    def convertFile(self, path: str, outputPath: str, inputFormat: str, outputFormat: str) -> bool:
        text = TextFile(path).load()

        if text is None:
            return False
        
        text = self.convert(text, inputFormat, outputFormat)

        if text is None:
            return False
        
        BinaryFile(outputPath).save(text.encode('utf-8'))
        return True
