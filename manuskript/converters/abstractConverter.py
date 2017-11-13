#!/usr/bin/env python
# --!-- coding: utf8 --!--


class abstractConverter:
    """
    A convertor is used to convert (duh) between stuff. They provide access
    to external libraries that may or may not be present.

    Now, things are a bit messy, since classes in `exporter` (and `importer` to a lesser extent) do
    the same. In a better world, classes from `exporter` and `importer` would
    use convertors to do their stuff. (TODO)
    """
    name = ""

    @classmethod
    def isValid(cls):
        return False
