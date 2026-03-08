#!/usr/bin/env python
# --!-- coding: utf8 --!--

from enum import Enum, unique


@unique
class PluginComponent(Enum):
    REQUIREMENTS = 0
    CONVERTERS = 1
    EXPORTERS = 2
    PLUGIN = 3
