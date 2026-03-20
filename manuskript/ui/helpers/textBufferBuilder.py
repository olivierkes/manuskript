#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import GLib, Gtk

class TextTag:
    tagName: str
    start: int
    end: int

    def __init__(self, tagName, start, end):
        self.tagName = tagName
        self.start = start
        self.end = end

    def __str__(self):
        return f"({self.tagName}, {self.start}, {self.end})"

class TextBufferBuilder:
    textParts: list[str]
    textTags: list[TextTag]=[]
    offset: int
    count: int

    def __init__(self):
        self.textParts: list[str]=[]
        self.textTags=[]
        self.offset=0
        self.count=0
        self.empties=0
        self.tagAdditions=0
        self.tagMerge=0
        self.lastTag: TextTag=None

    def append(self, text: str, tagName: str = None):
        if len(text) == 0:
            self.empties+=1
            return
        
        length=len(text)    
        nextOffset=self.offset + length
        if not tagName is None:
            self.tagAdditions+=1
            if self.lastTag and self.lastTag.end == self.offset and self.lastTag.tagName == tagName:
                self.lastTag.end = nextOffset
                self.tagMerge+=1
            else:
                self.lastTag = TextTag(tagName, self.offset, nextOffset)
                self.textTags.append(self.lastTag)                
        self.textParts.append(text)
        self.offset+=length
        self.count+=1

    def getLineCount(self) -> int:
        return self.count

    def render(self, buffer: Gtk.TextBuffer):
        fullText = "".join(self.textParts)
        buffer.set_text(fullText)

        for textTag in self.textTags:
            bufferTag = buffer.get_tag_table().lookup(textTag.tagName)
            start=buffer.get_iter_at_offset(textTag.start)
            end=buffer.get_iter_at_offset(textTag.end)
            buffer.apply_tag(bufferTag, start, end)


