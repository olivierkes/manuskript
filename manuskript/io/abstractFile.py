#!/usr/bin/env python
# --!-- coding: utf8 --!--


class AbstractFile:
    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> any:
        raise IOError("Loading undefined!")

    def save(self, content: any) -> None:
        raise IOError("Saving undefined!")

    def remove(self) -> None:
        raise IOError("Removing undefined!")
