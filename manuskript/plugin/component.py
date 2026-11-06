#!/usr/bin/env python
# --!-- coding: utf8 --!--

from enum import Enum, unique


@unique
class PluginComponent(Enum):
    REQUIREMENTS = 0
    CONVERTERS = 1
    IMPORTERS = 2
    EXPORTERS = 3
    REGIONERS = 4
    SPLITTERS = 5
    SPELLCHECKERS = 6
    PLUGIN = 7
