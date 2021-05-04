#!/usr/bin/env python
# --!-- coding: utf8 --!--

class UniqueID:

    def __init__(self, host, value: int):
        self.host = host
        self.value = value

    def __str__(self):
        return str(self.value)


class UniqueIDHost:

    def __init__(self):
        self.counter = 0
        self.uids = dict()

    def reset(self):
        self.counter = 0
        self.uids.clear()

    def newID(self):
        uid = UniqueID(self, self.counter)
        self.counter = self.counter + 1
        self.uids[uid.value] = uid
        return uid

    def loadID(self, value: int):
        if value in self.uids:
            raise ValueError("ID not unique: " + str(value))

        uid = UniqueID(self, value)
        self.counter = max(self.counter, uid.value + 1)
        self.uids[uid.value] = uid
        return uid

    def removeID(self, uid: UniqueID):
        if uid.host != self:
            raise ValueError("ID not bound to host!")

        self.uids.pop(uid.value)
