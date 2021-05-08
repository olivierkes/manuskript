#!/usr/bin/env python
# --!-- coding: utf8 --!--

import os

from manuskript.io.mmdFile import MmdFile


class Summary:

    def __init__(self, path):
        self.file = MmdFile(os.path.join(path, "summary.txt"), 13)

        self.sentence = None
        self.paragraph = None
        self.page = None
        self.full = None

    def load(self):
        metadata, _ = self.file.loadMMD(True)

        self.sentence = metadata.get("Sentence", None)
        self.paragraph = metadata.get("Paragraph", None)
        self.page = metadata.get("Page", None)
        self.full = metadata.get("Full", None)

    def save(self):
        metadata = dict()

        metadata["Sentence"] = self.sentence
        metadata["Paragraph"] = self.paragraph
        metadata["Page"] = self.page
        metadata["Full"] = self.full

        self.file.save((metadata, None))
