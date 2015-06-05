#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from __future__ import print_function
from __future__ import unicode_literals

def wordCount(text):
    return len(text.strip().split(" ")) if text else 0

def toInt(text):
    if text:
        return int(text)
    else:
        return 0
    
def toFloat(text):
    if text:
        return float(text)
    else:
        return 0.