#!/usr/bin/env python
# --!-- coding: utf8 --!--

import argparse
import json

url = "https://api.github.com/repos/{user}/{repo}/releases"

parser = argparse.ArgumentParser(description='Get download count for github releases.')
parser.add_argument('user', type=str, help='The github user.')
parser.add_argument('repo', type=str, help='The repo of given user.')
parser.add_argument("-d", "--details", action="store_true")

args = parser.parse_args()

url = url.format(user=args.user,
                 repo=args.repo)

def getJSON(URL):
    import urllib.request
    with urllib.request.urlopen(URL) as url:
        data = json.loads(url.read().decode())
        return data

def humanReadable(n):
    s = ["", "K", "M", "B", "T"]
    f = 1000.
    hrs = n
    i = 0
    while hrs > 500:
        hrs = hrs / f
        i += 1
    hrs = round(hrs, 1)
    return "{}{}".format(hrs, s[i])


def humanReadableSize(size):
    s = ["B", "KB", "MB", "GB", "TB"]
    f = 1024.
    hrs = size
    i = 0
    while hrs > 500:
        hrs = hrs / f
        i += 1
    hrs = round(hrs, 1)
    return "{} {}".format(hrs, s[i])

releases = getJSON(url)

total = 0

for r in releases:
    name = r["name"]
    tag = r["tag_name"]
    author = r["author"]["login"]
    time = r["created_at"]
    
    name = "{} ({})".format(name, tag) if name else tag
     
    tot = 0
    details = []
    for a in r["assets"]:
        nameA = a["name"]
        size = a["size"]
        download_count = a["download_count"]
        tot += download_count
        
        details.append("  *  {} ({}): {} hits".format(
            nameA, humanReadableSize(size), humanReadable(download_count))
        )
    
    txt = "{}: {} hits".format(name, humanReadable(tot))
    print(txt)
    if args.details:
        print("-" * len(txt))
        [print(d) for d in details]
        print("")
        
    total += tot

txt = "Total downloads: {} hits".format(humanReadable(total))
print("=" * len(txt))
print(txt)
print("=" * len(txt))