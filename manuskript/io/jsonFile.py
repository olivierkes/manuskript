#!/usr/bin/env python
# --!-- coding: utf8 --!--

import json
from manuskript.io.textFile import TextFile


class JsonFile(TextFile):

    def load(self):
        return json.loads(TextFile.load(self))

    def save(self, content):
        TextFile.save(self, json.dumps(content, indent=4, sort_keys=True))
