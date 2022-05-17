#!/usr/bin/env python
# --!-- coding: utf8 --!--
import re

from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtWidgets import qApp, QVBoxLayout, QCheckBox, QWidget, QHBoxLayout, QLabel, QSpinBox, QComboBox

from manuskript.exporter.manuskript.markdown import markdown, markdownSettings
from manuskript.ui.collapsibleGroupBox2 import collapsibleGroupBox2
from manuskript.functions import safeTranslate

import logging
LOGGER = logging.getLogger(__name__)


class abstractPlainText(markdown):
    name = "SUBCLASSME"
    description = "SUBCLASSME"
    exportVarName = "SUBCLASSME"
    toFormat = "SUBCLASSME"
    icon = "SUBCLASSME"
    exportFilter = "SUBCLASSME"
    exportDefaultSuffix = ".SUBCLASSME"

    def __init__(self, exporter):
        self.exporter = exporter

    def settingsWidget(self):
        # Get pandoc major version to determine valid command line options
        p = re.compile(r'pandoc (\d+)\.(\d+).*')
        m = p.match(self.exporter.version())
        if m:
            majorVersion = m.group(1)
            minorVersion = m.group(2)
        else:
            majorVersion = ""
            minorVersion = ""
        w = pandocSettings(self, majorVersion, minorVersion, toFormat=self.toFormat)
        w.loadSettings()
        return w

    def src(self, settingsWidget):
        return markdown.output(self, settingsWidget)

    def output(self, settingsWidget, outputfile=None):
        args = settingsWidget.runnableSettings()
        src = self.src(settingsWidget)
        return self.exporter.convert(src, args, outputfile)

    def preview(self, settingsWidget, previewWidget):
        settings = settingsWidget.getSettings()

        # Save settings
        settingsWidget.writeSettings()

        # Prepares text edit
        self.preparesTextEditViewMarkdown(previewWidget, settingsWidget.settings)
        self.preparesTextEditView(previewWidget, settings["Preview"]["PreviewFont"])

        r = self.output(settingsWidget)

        previewWidget.setPlainText(r)


def versionAsInt(version):
    if version is None:
        return 0

    try:
        return int(version)
    except ValueError:
        return 0


def versionToIntArray(version):
    if version is None:
        return [0, 0]

    p = re.compile(r'(\d+)\.(\d+).*')
    m = p.match(version)
    if m:
        majorVersion = m.group(1)
        minorVersion = m.group(2)
    else:
        majorVersion = ""
        minorVersion = ""

    return [ versionAsInt(majorVersion), versionAsInt(minorVersion) ]


class pandocSetting:
    def __init__(self, arg, type, format, label, widget=None, default=None, min=None, max=None, vals=None, suffix="",
                 minVersion=None, maxVersion=None, specific=False, toc=False):
        self.arg = arg  # start with EXT for extensions
        self.type = type
        self.label = label
        self.formats = format
        if "html" in self.formats:
            self.formats += " slidy dzslides revealjs slideous s5 html5"
        self.widget = widget
        self.default = default
        self.min = min
        self.max = max
        self.vals = vals.split("|") if vals else []
        self.suffix = suffix
        self.minVersion = versionToIntArray(minVersion)
        self.maxVersion = versionToIntArray(maxVersion)
        self.specific = specific
        self.toc = toc

    def isValid(self, format):
        """Return whether the specific setting is active with the given format."""

        # Empty formats means all
        if self.formats == "":
            return True

        # "html" in "html markdown latex"
        elif format in self.formats:
            return True

        # "markdown_strict" in "html markdown latex"
        elif [f for f in self.formats.split(" ") if format in f]:
            return True

        return False

    def isCompatible(self, majorVersion, minorVersion):
        majorNumber = versionAsInt(majorVersion)
        minorNumber = versionAsInt(minorVersion)

        if (majorNumber < self.minVersion[0]) or ((majorNumber == self.minVersion[0]) and
                                                  (minorNumber < self.minVersion[1])):
            return False

        if (self.maxVersion[0] == 0) and (self.maxVersion[1] == 0):
            return True

        return (majorNumber < self.maxVersion[0]) or ((majorNumber == self.maxVersion[0]) and
                                                      (minorNumber <= self.maxVersion[1]))

    def isSpecific(self):
        return self.specific

    def isTOC(self):
        return self.toc


class pandocSettings(markdownSettings):

    settingsList = {
        # General
        "standalone": pandocSetting("--standalone", "checkbox", "",
                                    safeTranslate(qApp, "Export", "Standalone document (not just a fragment)"),
                                    default=True),
        "TOC":          pandocSetting("--toc", "checkbox", "",
                                      safeTranslate(qApp, "Export", "Include a table of contents."), toc=True),

        "TOC-depth":    pandocSetting("--toc-depth=", "number", "",
                                      safeTranslate(qApp, "Export", "Number of sections level to include in TOC: "),
                                      default=3, min=1, max=6, toc=True, minVersion="1.10"),
        # pandoc v1 only
        "smart":        pandocSetting("--smart", "checkbox", "",
                                      safeTranslate(qApp, "Export", "Typographically correct output"),
                                      maxVersion="1.19.2.4"),
        # pandoc v1 only
        "normalize":    pandocSetting("--normalize", "checkbox", "",
                                      safeTranslate(qApp, "Export", "Normalize the document (cleaner)"),
                                      minVersion="1.8", maxVersion="1.19.2.4"),
        # pandoc v1.5 to 2.7.3
        "base-header": pandocSetting("--base-header-level=", "number", "",
                                     safeTranslate(qApp, "Export", "Specify the base level for headers: "),
                                     default=1, min=1, minVersion="1.5", maxVersion="2.7.3"),
        # pandoc v2.8+
        "shift-heading":  pandocSetting("--shift-heading-level-by=", "number", "",
                                      safeTranslate(qApp, "Export", "Specify the base level for headers: "),
                                      default=0, min=0, minVersion="2.8"),
        "disable-YAML": pandocSetting("EXT-yaml_metadata_block", "checkbox", "",
                                      safeTranslate(qApp, "Export", "Disable YAML metadata block.\nUse that if you get YAML related error."),
                                      minVersion="1.12"),
        "hard-line-breaks": pandocSetting("EXT-hard_line_block", "checkbox", "",
                                      safeTranslate(qApp, "Export", "Enable the support on markdown for line break on new line."),
                                      minVersion="1.16"),

        # Specific
        "ref-link":     pandocSetting("--reference-links", "checkbox", "markdown rst",
                                      safeTranslate(qApp, "Export", "Use reference-style links instead of inline links"),
                                      specific=True),
        # pandoc v1.9 to v2.11.1
        "atx":          pandocSetting("--atx-headers", "checkbox", "markdown asciidoc",
                                      safeTranslate(qApp, "Export", "Use ATX-style headers"), specific=True,
                                      minVersion="1.9", maxVersion="2.11.1"),
        # pandoc v2.11.2+
        "atx-heading": pandocSetting("--markdown-headings=atx|setext", "checkbox", "markdown asciidoc",
                                     safeTranslate(qApp, "Export", "Use ATX-style headers"), specific=True,
                                     minVersion="2.11.2"),
        "self-contained": pandocSetting("--self-contained", "checkbox", "html",
                                        safeTranslate(qApp, "Export", "Self-contained HTML files, with no dependencies"),
                                        specific=True, minVersion="1.9"),
        "q-tags":       pandocSetting("--html-q-tags", "checkbox", "html",
                                      safeTranslate(qApp, "Export", "Use <q> tags for quotes in HTML"), specific=True,
                                      minVersion="1.10"),
        # pandoc v1 only
        "latex-engine": pandocSetting("--latex-engine=", "combo", "pdf",
                                      safeTranslate(qApp, "Export", "LaTeX engine used to produce the PDF."),
                                      vals="pdflatex|lualatex|xelatex", specific=True,
                                      minVersion="1.9", maxVersion="1.19.2.4"),
        # pandoc v2
        "pdf-engine":   pandocSetting("--pdf-engine=", "combo", "pdf",
                                      safeTranslate(qApp, "Export", "LaTeX engine used to produce the PDF."),
                                      vals="pdflatex|lualatex|xelatex", minVersion="2.0", specific=True),
        "epub3":        pandocSetting("EXTepub3", "checkbox", "epub",
                                      safeTranslate(qApp, "Export", "Convert to ePUB3"), specific=True,
                                      minVersion="1.10"),

        # PDF
        "latex-ps":     pandocSetting("--variable=papersize:", "combo", "pdf latex",  # FIXME: does not work with default template
                                      safeTranslate(qApp, "Export", "Paper size:"),
                                      vals="letter|A4|A5", specific=True, minVersion="1.4"),
        "latex-fs":     pandocSetting("--variable=fontsize:", "number", "pdf latex",  # FIXME: does not work with default template
                                      safeTranslate(qApp, "Export", "Font size:"),
                                      min=8, max=88, default=12, suffix="pt", specific=True, minVersion="1.4"),
        "latex-class":  pandocSetting("--variable=documentclass:", "combo", "pdf latex",
                                     safeTranslate(qApp, "Export", "Class:"),
                                     vals="article|report|book|memoir", specific=True, minVersion="1.4"),
        "latex-ls":     pandocSetting("--variable=linestretch:", "combo", "pdf latex",
                                     safeTranslate(qApp, "Export", "Line spacing:"),
                                     vals="1|1.25|1.5|2", specific=True, minVersion="1.4"),

        # FIXME: complete with http://pandoc.org/README.html#variables-for-latex
    }


    def __init__(self, _format, majorVersion="", minorVersion="", toFormat=None, parent=None):
        markdownSettings.__init__(self, _format, parent)

        self.format = toFormat
        self.majorVersion = majorVersion
        self.minorVersion = minorVersion

        dropSettings = []

        for key, setting in self.settingsList.items():
            if not setting.isCompatible(self.majorVersion, self.minorVersion):
                dropSettings.append(key)

        LOGGER.info(f'Using pandoc settings: {self.majorVersion}.{self.minorVersion}, dropping: {dropSettings}')

        for key in dropSettings:
            self.settingsList.pop(key, None)

        w = QWidget(self)
        w.setLayout(QVBoxLayout())
        self.grpPandocGeneral = self.collapsibleGroupBox(self.tr("General"), w)
        self.grpPandocSpecific = self.collapsibleGroupBox(self.tr("Custom settings for {}").format(self.format), w)
        self.grpPandocTOC = self.collapsibleGroupBox(self.tr("Table of Content"), w)

        for key, setting in self.settingsList.items():
            if setting.isTOC():
                self.addSettingsWidget(key, self.grpPandocTOC)
            elif setting.isSpecific():
                self.addSettingsWidget(key, self.grpPandocSpecific)
            else:
                self.addSettingsWidget(key, self.grpPandocGeneral)

        self.toolBox.insertItem(self.toolBox.count() - 1, w, "Pandoc")
        self.toolBox.layout().setSpacing(0)  # Not sure why this is needed, but hey...

        self.getSettings()

    def collapsibleGroupBox(self, title, parent):
        g = collapsibleGroupBox2(title=title)
        parent.layout().addWidget(g)
        g.setLayout(QVBoxLayout())
        return g

    def addSettingsWidget(self, settingsName, parent):

        if not settingsName in self.settingsList:
            return

        s = self.settingsList[settingsName]

        if not s.isValid(self.format):
            # That setting is not available for that export format
            return

        if "checkbox" in s.type:
            s.widget = QCheckBox(s.label)
            if s.default:
                s.widget.setChecked(True)
            parent.layout().addWidget(s.widget)

        elif "number" in s.type:
            l = QHBoxLayout()
            label = QLabel(s.label, parent)
            label.setWordWrap(True)
            l.addWidget(label, 8)
            s.widget = QSpinBox()
            s.widget.setValue(s.default if s.default else 0)
            if s.min:
                s.widget.setMinimum(s.min)
            if s.max:
                s.widget.setMaximum(s.max)
            if s.suffix:
                s.widget.setSuffix(s.suffix)
            l.addWidget(s.widget, 2)
            parent.layout().addLayout(l)

        elif "combo" in s.type:
            l = QHBoxLayout()
            label = QLabel(s.label, parent)
            label.setWordWrap(True)
            l.addWidget(label, 6)
            s.widget = QComboBox()
            s.widget.addItems(s.vals)
            l.addWidget(s.widget, 2)
            parent.layout().addLayout(l)

    def updateFromSettings(self):
        markdownSettings.updateFromSettings(self)

        # s = self.settings["Preview"]
        # val = s.get("MarkdownHighlighter", False)
        # self.chkMarkdownHighlighter.setChecked(val)

        if not "Pandoc" in self.settings:
            return

        for name in self.settingsList:
            s = self.settingsList[name]

            if s.isValid(self.format):
                if s.type == "checkbox" and name in self.settings["Pandoc"]:
                    s.widget.setChecked(self.settings["Pandoc"][name])
                elif s.type == "number" and name in self.settings["Pandoc"]:
                    s.widget.setValue(int(self.settings["Pandoc"][name]))
                elif s.type == "combo" and name in self.settings["Pandoc"]:
                    s.widget.setCurrentText(self.settings["Pandoc"][name])


    def getSettings(self):
        self.settings = markdownSettings.getSettings(self)

        P = self.settings.get("Pandoc", {})

        for name in self.settingsList:
            s = self.settingsList[name]

            if s.isValid(self.format):
                if s.type == "checkbox":
                    P[name] = s.widget.isChecked()
                elif s.type == "number":
                    P[name] = str(s.widget.value())
                elif s.type == "combo":
                    P[name] = s.widget.currentText()

        self.settings["Pandoc"] = P

        return self.settings

    def runnableSettings(self):

        # First we get extensions (where arg starts with EXT)
        extensions = ""
        toFormat = self.format
        for name in self.settingsList:
            s = self.settingsList[name]
            if s.arg[:3] == "EXT" and s.isValid(self.format):
                if name == "disable-YAML" and s.widget.isChecked():
                    extensions += "-yaml_metadata_block"
                if name == "epub3" and s.widget.isChecked():
                    toFormat = "epub3"
                if name == "hard-line-breaks" and s.widget.isChecked():
                    extensions += "+hard_line_breaks"

        r = ["--from=markdown" + extensions,
             "--to={}".format(toFormat)]

        # Add every command
        for name in self.settingsList:
            s = self.settingsList[name]

            if s.arg[:3] == "EXT":
                continue

            if s.isValid(self.format):
                rr = ""
                if s.type == "checkbox":
                    if s.widget.isChecked():
                        rr = s.arg
                elif s.type == "number":
                    rr = "{}{}".format(
                        s.arg,
                        str(s.widget.value())
                    )
                elif s.type == "combo":
                    rr = "{}{}".format(
                        s.arg,
                        s.widget.currentText()
                    )

                if rr:
                    r.append(rr+s.suffix)
        return r

