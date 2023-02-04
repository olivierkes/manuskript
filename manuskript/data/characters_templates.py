#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

#from io.jsonFile import* # I need to figure out how to import this. io is also a package in python
from collections import OrderedDict


# So this is a template for character details
# It is edited by the Character Template Editor
# Most of the code is taken from characters.py
# I think this should have a custom save that's like a .json file in the main part of the manuskript save

#Main Class
class CharacterDetailTemplates:
# Basic Template
    templates = {'Basic Human':
                {'Age':'','Birthdate':'',
               'Eye Color':'','Hair Color':'',
               'Handed':''},
                }

 
    # TODO: saving
    def save(self):
        pass

    def load(self):
        pass

