#!/usr/bin/env python
# --!-- coding: utf8 --!--
import re

from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtWidgets import qApp, QVBoxLayout, QCheckBox, QWidget, QHBoxLayout, QLabel, QSpinBox, QComboBox

from manuskript.exporter.manuskript.markdown import markdown, markdownSettings
from manuskript.ui.collapsibleGroupBox2 import collapsibleGroupBox2


class abstractPlainText(markdown):
    name = "SUBCLASSME"
    description = "SUBCLASSME"
    exportVarName = "SUBCLASSME"
    toFormat = "SUBCLASSME"
    icon = "SUBCLASSME"
    exportFilter = "SUBCLASSME"

    def __init__(self, exporter):
        self.exporter = exporter

    def settingsWidget(self):
        # Get pandoc major version to determine valid command line options
        p = re.compile(r'pandoc (\d+)\..*')
        m = p.match(self.exporter.version())
        if m:
            majorVersion = m.group(1)
        else:
            majorVersion = ""
        w = pandocSettings(self, majorVersion, toFormat=self.toFormat)
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


class pandocSetting:
    def __init__(self, arg, type, format, label, widget=None, default=None, min=None, max=None, vals=None, suffix=""):
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

    def isValid(self, format):
        """Return whether the specific setting is active with the given format."""

        # Empty formats means all
        if self.formats is "":
            return True

        # "html" in "html markdown latex"
        elif format in self.formats:
            return True

        # "markdown_strict" in "html markdown latex"
        elif [f for f in self.formats.split(" ") if format in f]:
            return True

        return False


class pandocSettings(markdownSettings):

    settingsList = {
        # General
        "standalone": pandocSetting("--standalone", "checkbox", "",
                                    qApp.translate("Export", "Standalone document (not just a fragment)"),
                                    default=True),
        "TOC":          pandocSetting("--toc", "checkbox", "",
                                      qApp.translate("Export", "Include a table of contents.")),

        "TOC-depth":    pandocSetting("--toc-depth=", "number", "",
                                      qApp.translate("Export", "Number of sections level to include in TOC: "),
                                      default=3, min=1, max=6),
        # pandoc v1 only
        "smart":        pandocSetting("--smart", "checkbox", "",
                                      qApp.translate("Export", "Typographically correct output")),
        # pandoc v1 only
        "normalize":    pandocSetting("--normalize", "checkbox", "",
                                      qApp.translate("Export", "Normalize the document (cleaner)")),
        "base-header":  pandocSetting("--base-header-level=", "number", "",
                                      qApp.translate("Export", "Specify the base level for headers: "),
                                      default=1, min=1),
        "disable-YAML": pandocSetting("EXT-yaml_metadata_block", "checkbox", "",
                                      qApp.translate("Export", "Disable YAML metadata block.\nUse that if you get YAML related error.")),

        # Specific
        "ref-link":     pandocSetting("--reference-links", "checkbox", "markdown rst",
                                    qApp.translate("Export", "Use reference-style links instead of inline links")),
        "atx":          pandocSetting("--atx-headers", "checkbox", "markdown asciidoc",
                                    qApp.translate("Export", "Use ATX-style headers")),
        "self-contained": pandocSetting("--self-contained", "checkbox", "html",
                                        qApp.translate("Export", "Self-contained HTML files, with no dependencies")),
        "q-tags":       pandocSetting("--html-q-tags", "checkbox", "html",
                                        qApp.translate("Export", "Use <q> tags for quotes in HTML")),
        # pandoc v1 only
        "latex-engine": pandocSetting("--latex-engine=", "combo", "pdf",
                                      qApp.translate("Export", "LaTeX engine used to produce the PDF."),
                                      vals="pdflatex|lualatex|xelatex"),
        # pandoc v2
        "pdf-engine":   pandocSetting("--pdf-engine=", "combo", "pdf",
                                      qApp.translate("Export", "LaTeX engine used to produce the PDF."),
                                      vals="pdflatex|lualatex|xelatex"),
        "epub3":        pandocSetting("EXTepub3", "checkbox", "epub",
                                        qApp.translate("Export", "Convert to ePUB3")),
    }

    pdfSettings = {

        # PDF
        "latex-ps":     pandocSetting("--variable=papersize:", "combo", "pdf latex",  # FIXME: does not work with default template
                                      qApp.translate("Export", "Paper size:"),
                                      vals="letter|A4|A5"),
        "latex-fs":     pandocSetting("--variable=fontsize:", "number", "pdf latex",  # FIXME: does not work with default template
                                      qApp.translate("Export", "Font size:"),
                                      min=8, max=88, default=12, suffix="pt"),
        "latex-class":  pandocSetting("--variable=documentclass:", "combo", "pdf latex",
                                     qApp.translate("Export", "Class:"),
                                     vals="article|report|book|memoir"),
        "latex-ls":     pandocSetting("--variable=linestretch:", "combo", "pdf latex",
                                     qApp.translate("Export", "Line spacing:"),
                                     vals="1|1.25|1.5|2"),

        # FIXME: complete with http://pandoc.org/README.html#variables-for-latex
    }


    def __init__(self, _format, majorVersion="", toFormat=None, parent=None):
        markdownSettings.__init__(self, _format, parent)

        self.format = toFormat
        self.majorVersion = majorVersion

        w = QWidget(self)
        w.setLayout(QVBoxLayout())
        self.grpPandocGeneral = self.collapsibleGroupBox(self.tr("General"), w)

        if majorVersion == "1":
            # pandoc v1 only
            self.addSettingsWidget("smart", self.grpPandocGeneral)
            self.addSettingsWidget("normalize", self.grpPandocGeneral)
        else:
            # pandoc v2
            self.settingsList.pop("smart", None)
            self.settingsList.pop("normalize", None)
        self.addSettingsWidget("base-header", self.grpPandocGeneral)
        self.addSettingsWidget("standalone", self.grpPandocGeneral)
        self.addSettingsWidget("disable-YAML", self.grpPandocGeneral)

        self.grpPandocTOC = self.collapsibleGroupBox(self.tr("Table of Content"), w)

        self.addSettingsWidget("TOC", self.grpPandocTOC)
        self.addSettingsWidget("TOC-depth", self.grpPandocTOC)

        self.grpPandocSpecific = self.collapsibleGroupBox(self.tr("Custom settings for {}").format(self.format), w)

        self.addSettingsWidget("ref-link", self.grpPandocSpecific)
        self.addSettingsWidget("atx", self.grpPandocSpecific)
        self.addSettingsWidget("self-contained", self.grpPandocSpecific)
        self.addSettingsWidget("q-tags", self.grpPandocSpecific)
        if majorVersion == "1":
            # pandoc v1 only
            self.addSettingsWidget("latex-engine", self.grpPandocSpecific)
            self.settingsList.pop("pdf-engine", None)
        else:
            # pandoc v2
            self.settingsList.pop("latex-engine", None)
            self.addSettingsWidget("pdf-engine", self.grpPandocSpecific)
        self.addSettingsWidget("epub3", self.grpPandocSpecific)

        # PDF settings
        self.settingsList.update(self.pdfSettings)
        for i in self.pdfSettings:
            self.addSettingsWidget(i, self.grpPandocSpecific)

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

