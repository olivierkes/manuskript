#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import markdown
except ModuleNotFoundError:
    markdown = None

from manuskript.converter.abstractConverter import AbstractConverter


class MarkdownConverter(AbstractConverter):

    def __init__(self):
        AbstractConverter.__init__(self)

        self.inputFormats.append("plain")
        self.inputFormats.append("markdown")

        self.outputFormats.append("markdown")
        self.outputFormats.append("xhtml")
        self.outputFormats.append("html")

    def isValid(self) -> bool:
        return False if markdown is None else True

    def convert(self, text: str, inputFormat: str, outputFormat: str) -> str | None:
        if (inputFormat == "plain") and (output_format == "markdown"):
            return text
        elif (((inputFormat == "plain") or (inputFormat == "markdown")) and
              ((outputFormat == "xhtml") or (outputFormat == "html"))):
            return markdown.markdown(text, output_format=outputFormat)
        else:
            return AbstractConverter.convert(text, inputFormat, outputFormat)
