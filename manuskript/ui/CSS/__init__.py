from pathlib import Path
import re
from string import Formatter as F
class Formatter(F):
    def get_value(self, key, args, kwargs):
        try:
            return super().get_value(key, args, kwargs)
        except (KeyError, IndexError):
            return f"{{{key}}}"
f=Formatter()
Folder=Path(__file__).parent
names:dict[str,str]={}
"""in case we want to change what filenames are saved as in our dict"""
class strformat(str):
    'Allows unamed parameters'
    def format(self, *args: object, **kwargs: object) -> 'strformat':
        return strformat(f.vformat(self, args, kwargs))
stylesheets:dict[str,strformat]={}
def loadfile(path:Path):
    if path.suffix!='.css'or  not path.is_file():return
    return preparecss(path.read_text())
def preparecss(s):
    s = re.sub(r'{(?![a-zA-Z_])', '{{', s)
    return strformat(re.sub(r'(?<![a-zA-Z0-9_])}', '}}', s))
def loadfiles(stylesheets:dict|None=stylesheets, subnames:dict[str,str]|None=names):
    if not isinstance(stylesheets, dict):
        stylesheets={}
    if not isinstance(subnames, dict):
        subnames={}
    for dirpath, _, filenames in Folder.walk():
        for filename in filenames:
            text=loadfile(dirpath.joinpath(filename))
            if text is not None:
                name=subnames.get(filename, filename)
                stylesheets[name]=text
                stylesheets[name.removesuffix('.css')]=text
    return stylesheets
def get(name, onfail=''):
    return stylesheets.get(name) or stylesheets.get(name.removesuffix('.css'),strformat(onfail))
def css_to_dict(css: str) -> dict[str, strformat]:
    css=strformat(css)
    sections = {'':css}
    current = None
    lines = []
    for line in css.splitlines():
        m = re.fullmatch(r"\s*/\*\s*(.*?)\s*\*/\s*", line)
        if m:
            if current is not None:
                sections[current] = strformat("\n".join(lines).strip())
            current = m.group(1)
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = strformat("\n".join(lines).strip())
    return sections
stylesheets.update(loadfiles())
