#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The idea was to find icons duplicates in size, but there aren't many.
"""

import os
dir_path = os.path.dirname(os.path.realpath(__file__))

numix = os.path.join(dir_path, "NumixMsk")
scalable = os.path.join(numix, "scalable")

dupes = {}

for path, dirs, files in os.walk(numix):
    if path == numix or not files:
        continue


    foldername = os.path.basename(path) # mimetype, places, actions, etc.
    size = os.path.basename(os.path.split(path)[0]) # 32x32 64x64
    print(size, foldername)

    for f in files:
        fullname = os.path.join(path, f)

        if not f in dupes:
            dupes[f] = [foldername]
        dupes[f].append(size)

        #scalable_path = os.path.join(scalable, foldername, f)
        ##print(" * ", scalable_path)

        #if os.path.exists(scalable_path):
            #s1 = os.path.getsize(fullname)
            #s2 = os.path.getsize(scalable_path)

            #if s1 == s2:

                #if not f in dupes:
                    #dupes[f] = [foldername]
                #else:
                    #dupes[f].append(foldername)

#print(dupes)

print("ICONS IN ONLY ONE SIZE")

for d in dupes:
    foldername = dupes[d][0]
    sizes = dupes[d][1:]
    sizes = sorted(sizes, key=lambda s: int(s.split("x")[0]) if "x" in s else 1000)

    if len(sizes) == 1:
        print(os.path.join(sizes[0], foldername, d))
        #print("mkdir -p NumixMsk/{}".format(os.path.join("scalable", foldername)))
        #print("cp NumixMsk/{} NumixMsk/{}".format(
            #os.path.join(sizes[0], foldername, d),
            #os.path.join("scalable", foldername))
        #)

    if len(sizes) < 2:
        continue

    #print(d, "({})".format(foldername))
    #print("-" * len(d))
    #for s in sizes:
        #f = os.path.join(numix, s, foldername, d)
        #size = os.path.getsize(f)
        #print(" * {} ({})".format(s, size))
    #print()

