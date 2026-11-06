#!/usr/bin/env python
# --!-- coding: utf8 --!--


class UniqueID:
    def __init__(self, host: UniqueIDHost, value: int) -> None:
        self.host = host
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return self.value


class UniqueIDHost:
    def __init__(self) -> None:
        self.counter = 0
        self.uids = dict()

    def reset(self) -> None:
        self.counter = 0
        self.uids.clear()

    def newID(self) -> UniqueID:
        uid = UniqueID(self, self.counter)
        self.counter = self.counter + 1
        self.uids[uid.value] = uid
        return uid

    def loadID(self, value: int) -> UniqueID:
        if value in self.uids:
            raise ValueError("ID not unique: " + str(value))

        uid = UniqueID(self, value)
        self.counter = max(self.counter, uid.value + 1)
        self.uids[uid.value] = uid
        return uid

    def removeID(self, uid: UniqueID) -> None:
        if uid.host != self:
            raise ValueError("ID not bound to host!")

        self.uids.pop(uid.value)
