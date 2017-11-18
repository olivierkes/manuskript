#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for outlineItem"""


def square(i):
    return i*i

def test_square():
    assert square(2) == 4
    assert square(-2) == 4
