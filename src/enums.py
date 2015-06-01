#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

# As seen on http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python

from enum import Enum

#def enum(**enums):
    #return type(str('Enum'), (), enums)

class Perso(Enum):
    name = 0
    ID = 1
    importance = 2
    motivation = 3
    goal = 4
    conflict = 5
    epiphany = 6
    summarySentance = 7
    summaryPara = 8
    summaryFull = 9
    notes = 10
    
