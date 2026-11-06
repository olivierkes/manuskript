#!/usr/bin/env python
# --!-- coding: utf8 --!--

import re


class Color:
    def __init__(self, red: int, green: int, blue: int) -> None:
        self.red = red
        self.green = green
        self.blue = blue

    def getRGB(self) -> int:
        return (self.red << 24) | (self.green << 16) | (self.blue << 8)

    def __str__(self) -> str:
        return "#%02x%02x%02x" % (self.red, self.green, self.blue)

    @classmethod
    def parse(cls, string: str | None) -> Color | None:
        if string is None:
            return None

        colorPattern = re.compile(r"\#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})")

        m = colorPattern.match(string)

        if m is None:
            return None

        return Color(int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16))
