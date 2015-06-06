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
    
    
class Outline(Enum):
    title = 0
    ID = 1
    type = 2
    summarySentance = 3
    summaryFull = 4
    POV = 5
    notes = 6
    status = 7
    compile = 8
    text = 9
    wordCount = 10
    goal = 11
    goalPercentage = 12
    setGoal = 13 # The goal set by the user, if any. Can be different from goal which can be computed
                 # (sum of all sub-items' goals)
    textFormat = 14
