#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

realpath = os.path.realpath(__file__)

sys.path.insert(1, os.path.join(os.path.dirname(realpath), '..'))

import manuskript.data as data
import manuskript.load_save.version_1 as v1

path = os.path.join(sys.path[1], "sample-projects/book-of-acts")

import time

start = time.time()

project = data.Project(path + ".msk")
project.load()

end = time.time()
duration = end - start

print(duration)

project.save()
