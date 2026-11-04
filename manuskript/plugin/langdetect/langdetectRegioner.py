#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import langdetect
except ModuleNotFoundError:
    langdetect = None

from manuskript.editor.abstractRegioner import AbstractRegioner
from manuskript.editor.splitResult import SplitResult


class LangdetectRegioner(AbstractRegioner):

    def __init__(self):
        AbstractRegioner.__init__(self, [
          "af", "ar", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "es", "et", "fa", "fi", "fr", "gu", "he",
          "hi", "hr", "hu", "id", "it", "ja", "kn", "ko", "lt", "lv", "mk", "ml", "mr", "ne", "nl", "no", "pa", "pl",
          "pt", "ro", "ru", "sk", "sl", "so", "sq", "sv", "sw", "ta", "te", "th", "tl", "tr", "uk", "ur", "vi",
          "zh-cn", "zh-tw"
        ])

    def isValid(self) -> bool:
        return langdetect is not None

    def splitText(self, text: str) -> SplitResult:
        result: SplitResult = AbstractRegioner.splitText(self, text)

        for tuple in result.tuples:
          region: str = result.text[tuple.begin:tuple.end]
          tuple.lang = langdetect.detect(region)

        return result
