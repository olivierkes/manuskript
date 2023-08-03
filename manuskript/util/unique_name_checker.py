#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# So this thing changes a name until it works with a dictionary
# Ie. if you have a dictioary {'Item':1,'Item2':1,'Item3':1} and if you add an item it'll be Item4
# It works only on strings

def get_unique_name_for_dictionary(dictionary, name):
    count = 1
    test_name = name
    while test_name in dictionary:
        count += 1
        test_name = str(name) +(str(count))
        
    return test_name

