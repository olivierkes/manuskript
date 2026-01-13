#!/usr/bin/env python
# --!-- coding: utf8 --!--


class AbstractConverter:

    def __init__(self):
        self.inputFormats = []
        self.outputFormats = []

    def supportsInput(self, format: str) -> bool:
        return format in self.inputFormats

    def supportsOutput(self, format: str) -> bool:
        return format in self.outputFormats

    def convert(self, text: str, inputFormat: str, outputFormat: str) -> str | None:
        if inputFormat == outputFormat:
            return text
        else:
            return None
