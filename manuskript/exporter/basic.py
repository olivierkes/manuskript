#!/usr/bin/env python
# --!-- coding: utf8 --!--

import shutil
import subprocess

from PyQt5.QtWidgets import QWidget

from manuskript.models.outlineModel import outlineItem


class basicExporter:

    name = ""
    description = ""
    exportTo = []
    cmd = ""

    def __init__(self):
        pass

    @classmethod
    def getFormatByName(cls, name):
        for f in cls.exportTo:
            if f.name == name:
                return f

        return None

    @classmethod
    def isValid(cls):
        return cls.path() != None

    @classmethod
    def version(cls):
        return ""

    @classmethod
    def path(cls):
        return shutil.which(cls.cmd)

    @classmethod
    def run(cls, args):
        r = subprocess.check_output([cls.cmd] + args)  # timeout=.2
        return r.decode("utf-8")

        # Example of how to run a command
        #
        # cmdl = ['txt2tags', '-t', target, '--enc=utf-8', '--no-headers', '-o', '-', '-']
        #
        # cmd = subprocess.Popen(('echo', text), stdout=subprocess.PIPE)
        # try:
        #     output = subprocess.check_output(cmdl, stdin=cmd.stdout, stderr=subprocess.STDOUT)  # , cwd="/tmp"
        # except subprocess.CalledProcessError as e:
        #     print("Error!")
        #     return text
        # cmd.wait()
        #
        # return output.decode("utf-8")


class basicFormat:

    implemented = False
    requires = {
        "Settings": False,
        "PreviewBefore": False,
        "PreviewAfter": False,
    }

    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    @classmethod
    def settingsWidget(cls):
        return QWidget()

    @classmethod
    def previewWidgetBefore(cls):
        return QWidget()

    @classmethod
    def previewWidgetAfter(cls):
        return QWidget()

    @classmethod
    def concatenate(cls, item:outlineItem,
                    processTitle=lambda x: x + "\n",
                    processText=lambda x: x + "\n",
                    processContent=lambda x: x + "\n",
                    textSep="", folderSep="", textFolderSep="", folderTextSep="") -> str:

        r = ""

        if not item.compile():
            return ""

        if item.level() >= 0:  # item is not root

            # Adds item title
            r += processTitle(item.title())

            # Adds item text
            r += processText(item.text())

        content = ""

        # Add item children
        last = None
        for c in item.children():

            # Separator
            if last:
                # Between folder
                if last == c.type() == "folder":
                    content += folderSep
                elif last == c.type() == "md":
                    content += textSep
                elif last == "folder" and c.type() == "md":
                    content += folderTextSep
                elif last == "md" and c.type() == "folder":
                    content += textFolderSep

            content += cls.concatenate(c)

            last = c.type()

        r += processContent(content)

        return r