#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gettext
from io import StringIO
import langcodes
import locale
import os


class Translation:

  def __init__(self, language: str|None = None, domain: str = "manuskript", locale_dir: str|None = None):
    self.language = Translation.getDefaultLanguage() if language is None else language
    self.domain = domain
    self.locale_dir = Translation.getAppLocaleDirectory() if locale_dir is None else locale_dir
    self.translation = None

    print(self.language)

    def isLocalizationFile(filename: str) -> bool:
      path = os.path.join(self.getLocaleDirectory(), filename)

      if not os.path.isdir(path):
        return False

      localization_path = os.path.join(path, "LC_MESSAGES/" + self.getDomain() + ".mo")
      return os.path.isfile(localization_path)

    locale_files: list[str] = os.listdir(self.getLocaleDirectory())
    self.languages: list[str] = [f for f in filter(isLocalizationFile, locale_files)]

    self.setLanguage(self.getLanguage())

  def getLanguage(self) -> str:
    return self.language

  def setLanguage(self, language: str):
    self.language = language

    if language in self.getSupportedLanguages():
      self.translation = gettext.translation(
        self.getDomain(),
        localedir=self.getLocaleDirectory(),
        languages=[self.getLanguage()],
        fallback=True
      )
    else:
      self.translation = None

  def getDomain(self) -> str:
    return self.domain

  def getLocaleDirectory(self) -> str:
    return self.locale_dir

  def getSupportedLanguages(self) -> list[str]:
    return self.languages

  def bind(self):
    try:
      locale.bindtextdomain(self.getDomain(), self.getLocaleDirectory())
      locale.bind_textdomain_codeset(self.getDomain(), "UTF-8")
      locale.textdomain(self.getDomain())
    finally:
      gettext.bindtextdomain(self.getDomain(), self.getLocaleDirectory())
      gettext.textdomain(self.getDomain())

  def translate(self, message: str, plural_message: str|None = None, n: int = 1) -> str:
    if self.translation is None:
      if plural_message is None:
        return message
      else:
        return message if n <= 0 else plural_message
    else:
      if plural_message is None:
        return self.translation.gettext(message)
      else:
        return self.translation.ngettext(message, plural_message, n)

  @classmethod
  def getAppLocaleDirectory(cls) -> str:
    realpath = os.path.realpath(__file__)
    app_path = os.path.join(os.path.dirname(realpath), '../..')
    locale_dir = os.path.join(app_path, 'locale')
    return os.path.realpath(locale_dir)

  @classmethod
  def getDefaultLanguage(cls) -> str:
    current_locale: tuple[str|None, str|None] = locale.getlocale(locale.LC_MESSAGES)
    locale_id: str|None = current_locale[0]

    if locale_id is None:
      return "en"

    index: int = locale_id.find('_')
    if index < 0:
      return locale_id
    else:
      return locale_id[:index]

  @classmethod
  def getLanguageName(cls, language: str, autonym: bool = False) -> str:
    try:
      index: int = language.find('@')
      name: str = language
      specifier: str = ""

      if index >= 0:
        specifier = language[index+1:]
        name = language.replace('@', '-')

      lang: langcodes.Language = langcodes.Language.get(name)
      if autonym:
        name = lang.autonym()

        if len(name) > 0:
          s = StringIO()

          s.write(name[0].upper())
          s.write(name[1:].lower())

          name = s.getvalue()
      else:
        name = lang.display_name()

      lower_name: str = name.lower()
      if (len(specifier) > 0) and (not specifier.lower() in lower_name):
        s = StringIO()

        s.write(name)
        s.write(" (")
        s.write(specifier)
        s.write(")")

        name = s.getvalue()

      index = name.find('(')
      if (index >= 0) and (name.find(')') > index + 1):
        s = StringIO()

        s.write(name[:index + 1])
        s.write(name[index + 1].upper())
        s.write(name[index + 2:])

        name = s.getvalue()

      return name
    except ModuleNotFoundError:
      return language
