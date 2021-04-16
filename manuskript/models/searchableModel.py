#!/usr/bin/env python
# --!-- coding: utf8 --!--


class searchableModel():

    def searchOccurrences(self, searchRegex, columns):
        results = []
        for item in self.searchableItems():
            for column in columns:
                results += item.searchOccurrences(searchRegex, column)
        return results

    def searchableItems(self):
        raise NotImplementedError
