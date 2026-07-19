#!/usr/bin/env python
# --!-- coding: utf8 --!--

from enum import Enum, unique


@unique
class PluginComponent(Enum):
    REQUIREMENTS = 0
    CONVERTERS = 1
    EXPORTERS = 2
    REGIONERS = 3
    SPLITTERS = 4
    SPELLCHECKERS = 5
    PLUGIN = 6
