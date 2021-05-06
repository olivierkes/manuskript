#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

realpath = os.path.realpath(__file__)

sys.path.insert(1, os.path.join(os.path.dirname(realpath), '..'))

import manuskript.io as io
import manuskript.data as data

path = os.path.join(sys.path[1], "sample-projects/book-of-acts")

#project = data.Project(path + ".msk")
#project.load()

#settings = project.settings

#print(settings.properties)

#plots = project.plots

#revs = project.revisions

#for status in project.statuses:
#    print("--" + str(status))

#settings.set("saveToZip", True)
#project.save()

#settings.set("saveToZip", False)
#project.save()

mmd = io.MmdFile(path + "/outline/0-Jerusalem/0-Chapter_1/0-Introduction.md")

meta, _ = mmd.loadMMD()

print(meta)

meta, body = mmd.load()

print(meta)
print(body)

mmd.save((meta, body))
