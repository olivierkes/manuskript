#!/usr/bin/env python
# --!-- coding: utf8 --!--

try:
    import markdown
except ModuleNotFoundError:
    markdown = None

from manuskript.plugin import AbstractPlugin
from manuskript.plugin.markdown.markdownConverter import MarkdownConverter


class MarkdownPlugin(AbstractPlugin):

    def __init__(self):
        super().__init__()
    
    def preload(self) -> bool:
        if not markdown:
            return False
        
        self.registerConverter(MarkdownConverter)
        return True
