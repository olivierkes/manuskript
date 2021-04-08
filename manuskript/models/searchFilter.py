#!/usr/bin/env python
# --!-- coding: utf8 --!--


class searchFilter:
    def __init__(self, label, enabled, modelColumns = None):
        if not isinstance(label, str):
            raise TypeError("label must be a str")

        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool")

        if modelColumns is not None and (not isinstance(modelColumns, list)):
            raise TypeError("modelColumns must be a list or None")

        self._label = label
        self._enabled = enabled
        self._modelColumns = modelColumns
        if self._modelColumns is None:
            self._modelColumns = []

    def label(self):
        return self._label

    def enabled(self):
        return self._enabled

    def modelColumns(self):
        return self._modelColumns

    def setEnabled(self, enabled):
        self._enabled = enabled
