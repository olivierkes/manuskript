#!/usr/bin/env python
# --!-- coding: utf8 --!--


class abstractSearchResultHighlighter():
    """
    Interface for all classes highlighting search results on widgets.
    """
    def __init__(self):
        pass

    def highlightSearchResult(self, searchResult):
        raise NotImplementedError
