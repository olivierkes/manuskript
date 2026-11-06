#!/usr/bin/env python
# --!-- coding: utf8 --!--


from typing import Any


class AbstractFile:
    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> Any:
        raise IOError("Loading undefined!")

    def save(self, content: Any) -> None:
        raise IOError("Saving undefined!")

    def remove(self) -> None:
        raise IOError("Removing undefined!")
