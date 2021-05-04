#!/usr/bin/env python
# --!-- coding: utf8 --!--


class AbstractFile:

    def __init__(self, path):
        self.path = path

    def load(self):
        raise IOError('Loading undefined!')

    def save(self, content):
        raise IOError('Saving undefined!')
