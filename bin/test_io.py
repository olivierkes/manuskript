#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

realpath = os.path.realpath(__file__)

sys.path.insert(1, os.path.join(os.path.dirname(realpath), '..'))

import manuskript.io as io
import manuskript.data as data

path = os.path.join(sys.path[1], "sample-projects/book-of-acts/settings.txt")

settings = io.JsonFile(path)
result = settings.load()

print(result)

plots = data.Plots(os.path.join(sys.path[1], "sample-projects/book-of-acts/plots.xml"))

plots.load()
plots.save()
