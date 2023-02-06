#!/usr/bin/env python
# --!-- coding: utf8 --!--

from collections.abc import Callable
from enum import Enum, unique

from manuskript.data.unique_id import UniqueID


@unique
class LinkAction(Enum):
    DELETE = 0
    UPDATE = 1
    RELOAD = 2


class Links:

    def __init__(self):
        self.callbacks = list()

    def add(self, callback: Callable[[LinkAction, UniqueID, any], None]):
        self.callbacks.append(callback)

    def remove(self, callback: Callable[[LinkAction, UniqueID, any], None]):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def call(self, action: LinkAction, UID: UniqueID, host: any):
        for callback in self.callbacks:
            callback(action, UID, host)

        if action == LinkAction.DELETE:
            self.callbacks.clear()
