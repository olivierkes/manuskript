#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import langdetect
except ModuleNotFoundError:
    langdetect = None

from manuskript.plugin import AbstractPlugin
from manuskript.plugin.langdetect.langdetectRegioner import LangdetectRegioner


class LangdetectPlugin(AbstractPlugin):

    def __init__(self):
        super().__init__()

    def preload(self) -> bool:
        if not langdetect:
            return False

        self.registerRegioner(LangdetectRegioner)
        return True
