import re, importlib
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from typing import (Any, overload,Callable, Literal,Iterable, TYPE_CHECKING, Sequence, Mapping, TypeVar,Optional, IO)
from types import ModuleType
from pathlib import Path
from atexit import register
_A=TypeVar('_A')
use_language_check = False
SYMSPELLPY_MIN_VERSION = "6.3.8"
symspellpymod=None
EMPTYMODULE=ModuleType('Empty',)
missing=object()
import subprocess
def tag(func=None,isAtrr=False, isHint=False, isPriority=False, isRaise=False):
    def decorate(function):
        return function
    return decorate
def pipmode(m=0):
    'in some case, due to how python is addded to path, python, py or pip commands arent available'
    match m:
        case 3:
            from sys import executable
            return [repr(executable), '-m pip']# I saw somewhere this might be safest, Oh well, I prefer 'pip' because i remember an alwful school laptop that never added python to path, and pip was all I had
        case 2:
            return ['python',  '-m pip']
        case 1:
            return ['py', '-m pip']
        case 0:
            return ['pip']
        case _:
            return ['pip']
def inspectCall(includeself:bool|int=False):
    i=2-includeself# if we are 2, skip ourself (inspectCall) and whatever directly called us, 1 only skips ourself
    import inspect
    def frameText(frame):
        return f'File "{frame.filename.replace('/', '\\')}", line {frame.lineno}, in {frame.function}'
    for frame in inspect.stack()[i:]:
        print(frameText(frame))
from PyQt5.QtCore import QObject, pyqtSignal
class Waiter(QObject):
    start = pyqtSignal(type)

    def __init__(self):
        super().__init__()
        self.do = []
        self.start.connect(self.act)

    def add(self, name, *args, **kwargs):
        self.do.append((name, args, kwargs))

    def act(self, cls):
        try:
            for name, args, kwargs in self.do:
                method = getattr(cls, name, None)
                if callable(method):
                    method(*args, **kwargs)
        finally:
            self.do.clear()
            self.deleteLater()
class InstallerWorker(QObject):
    log = pyqtSignal(str)
    moduleFinished = pyqtSignal(str, bool)
    finished = pyqtSignal()
    cachedInstalls={}
    def __init__(self, modulenames, trusted=False):
        super().__init__()
        self.modulenames = list(modulenames)
        self.trusted = trusted
        self.results:dict[str, bool] = {}
    def __hash__(self) -> int:
        return id(self)
    def cache(self, thread=None):
        self.cachedInstalls[self]= thread or  self.thread()
    def decache(self):
        self.cachedInstalls.pop(self, None)
    def install(self, module: str) -> int:
        # Five attempts, allowing different pip modes.
        for attempt in range(5):
            command = pipmode(attempt) + ["install", module]

            if self.trusted:
                command += ["--trusted-host", "pypi.org", "--trusted-host", "files.pythonhosted.org"]
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                self.log.emit(result.stdout)

                if result.stderr:
                    self.log.emit(result.stderr)

                return result.returncode

            except FileNotFoundError as exc:
                self.log.emit(f"Attempt {attempt + 1}: {exc};\n command was {command!r}")


        raise FileNotFoundError(f"No usable pip command found for {module}")

    @pyqtSlot()
    def run(self):
        try:
            for module in self.modulenames:
                self.log.emit(f"Installing {module}...")

                try:
                    code = self.install(module)
                    success = code == 0
                except Exception as exc:
                    self.log.emit(f"Installation error: {exc}")
                    success = False

                self.results[module] = success
                self.moduleFinished.emit(module, success)

        finally:
            self.finished.emit()
    @classmethod
    def startInstallation(cls, modulenames, trusted=False, parent=None):
        installThread = QThread(parent)
        installWorker = InstallerWorker(modulenames, trusted)
        installWorker.moveToThread(installThread)
        installWorker.cache(installThread)
        installThread.started.connect(installWorker.run)
        installWorker.moduleFinished.connect(lambda module, success: print(f"{'Successfully installed' if success else 'Failed to install'} {module}"))
        installWorker.finished.connect(installThread.quit)
        installWorker.finished.connect(installWorker.deleteLater)
        installThread.finished.connect(installThread.deleteLater)
        installThread.finished.connect(installWorker.decache)
        installThread.start()
        return installWorker
def getVersion(module:ModuleType)->str:
    _version=getattr(module, '__version__', None)
    def fromPackaging(_version=_version):
        try:
            from packaging.version import Version # pyright: ignore[reportMissingImports]
            if _version:
                return str(Version(_version))
        except ImportError:
            pass
    def fromDistutils(_version=_version):
        try:
            import distutils.version # pyright: ignore[reportMissingImports]
            if _version:
                return str(distutils.version.LooseVersion(_version))
        except ImportError:
            pass
    def fromImportlib(_version=_version):
        try:
            from importlib.metadata import version # pyright: ignore[reportMissingImports]
            return version(module.__name__.rpartition('.')[-1])   
        except ImportError:
            pass
    
    for m in (fromPackaging, fromDistutils, fromImportlib):
        v=m()
        if v is not None:
            return v
    return '0.0.0'
class MetaModule(type):
    @classmethod
    def __prepare__(mcls,*args, **kwargs):
        waiter = Waiter()
        def tag(func=None, *args,isAtrr=False, isHint=False, isPriority=False, isRaise=False, **kwargs):
            if func is None:
                return lambda f: tag(f, *args,isAtrr=isAtrr, isHint=isHint, isPriority=isPriority, isRaise=isRaise, **kwargs)            
            waiter.add("_tag", func, *args,isAtrr=isAtrr, isHint=isHint, isPriority=isPriority, isRaise=isRaise, **kwargs)
            return func
        return {"waiter":waiter, "tag":tag}
    def _tag(self):
        pass
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)        
        waiter:None|Waiter = namespace.get("waiter")
        if waiter is not None:
            waiter.start.emit(cls)
        return cls

class BaseModule(ModuleType, metaclass=MetaModule):
    LibraryRequirement=''
    LibraryURL=''
    LibraryName=''
    _basemodule = EMPTYMODULE
    __attrs__:set[str] = {"_basemodule","__attrs__","__typehintattrs__","__eq__","isValid",'__raise__', '__prioritise__', '__install__'}
    "attributes that belong to the wrapper itself, and should not be looked for in _basemodule"
    __typehintattrs__:set[str] = set()
    "attributes that are 'implemented' BaseModule, but should be looked for in _basemodule first"
    __raise__:set[str]=set()
    "__typehintattrs__ that raise instead of looking in BaseModule"
    __prioritise__:set[str]={'__name__', 'LibraryName', 'LibraryURL','LibraryRequirement'}    
    "attributes that should be looked for in the wrapper itself, but different from __attrs__ in that its fine to look in _basemodule"   

    def __init__(self,name: str,doc: str | None = None,basename:  str | None|tuple[str, ...] = None,module: ModuleType | None|str = None) -> None:
        """
        Initializes a BaseModule wrapper around a real Python module.

        Resolution priority for `_basemodule`:

        1. If `module` is provided and is a ModuleType:
        - Use it directly as the backend module.

        2. If `basename` is a tuple:
        - Treat it as a list of candidate module names.
        - Optionally append `name` (or `module` if it is a string).
        - Attempt to import each candidate in order until one succeeds.

        3. If `basename` is a string:
        - Import that module directly.

        4. Otherwise:
        - Import the module using `name`.

        Failure behavior:
        - If all import attempts fail, `_basemodule` is not set to a valid module.
        - A failure message is printed indicating the attempted module name(s).
        """
        super().__init__(name, doc)
        # def ifmodule():
        #     if isinstance(module, ModuleType):
        #         self._basemodule=module
        #         return True
        #     return False
        # def iftuple(basename=basename):
        #     if isinstance(basename, tuple):
        #         basename+=(name,) if not isinstance(module, str) else (module, name)
        #         for b in basename:
        #             try:
        #                 self._basemodule=importlib.import_module(b)   
        #                 return True
        #             except Exception:pass
        #     return False
        # def ifstr():
        #     if isinstance(basename, str):
        #         self._basemodule=importlib.import_module(basename)  
        #         return True
        #     return False
        # def iffail():
        #     try:
        #         self._basemodule=importlib.import_module(name)  
        #         return True
        #     except Exception:
        #         return False
        # for method in (ifmodule, iftuple,ifstr,iffail):
        #     try:
        #         if method() :
        #             break
        #     except Exception:
        #         pass
        # else:
        #     print(f"Failed to load {basename or name}")
        try:
            printing=False#isinstance(self, (MODMD, SYMSPELLPY))
            if printing:
                print(name, basename, module)
            if isinstance(module, ModuleType):
                self._basemodule=module
            elif isinstance(basename, tuple):
                basename+=(name,) if not isinstance(module, str) else (module, name)
                for b in basename:
                    try:
                        self._basemodule=importlib.import_module(b)   
                        return
                    except Exception:pass
            elif isinstance(basename, str):
                if printing:
                    print(f'usind basename, {basename}')
                self._basemodule=importlib.import_module(basename, package=None)  
            else:
                print(name)
                self._basemodule=importlib.import_module(name)  
        except Exception as e:
            if basename or name:
                print(f"Failed to load {basename or name}")
    def __init_subclass__(cls,attrs=(),attrs_override=False,hints=(),hints_override=False,raises=(),raises_override=False,priorities=(),priorities_override=False, parent:type['BaseModule']|None=None) -> None:
        if not isinstance(parent, type) or not issubclass(parent, BaseModule):
            parent=BaseModule
        if attrs_override:
            cls.__attrs__=BaseModule.__attrs__.union(attrs)
        else:
            cls.__attrs__=parent.__attrs__.union(attrs)
        if hints_override:
            cls.__typehintattrs__=set(hints)
        else:
            cls.__typehintattrs__=parent.__typehintattrs__.union(hints)
        if raises_override:
            cls.__raise__=set(raises)
        else:
            cls.__raise__=parent.__raise__.union(raises)
        if priorities_override:
            cls.__prioritise__=set(priorities)
        else:
            cls.__prioritise__=parent.__prioritise__.union(priorities)
    def __getattribute__(self, name: str) -> Any:
        """
        1. If name is listed in __attrs__, return the attribute from self
        directly (This has no error handling).
        1. If name is listed in __prioritise__, return the attribute from self unless there is an error, in which case continue to attempt the following.
        
        2. Otherwise, attempt to retrieve the attribute from _basemodule.
        3. If _basemodule lookup fails:
        - a. If name is listed in __typehintattrs__, return the local implementation from self.\n
        - b. Otherwise, re-raise the original AttributeError from _basemodule.
        4. If name is listed in __raise__, always raise the original error even if a fallback exists.
        """
        def safeget(name, default:Any=missing):
            return safegetter(self, name,default)
        failed=False
        notes:list[str]=[]
        if name in safeget("__attrs__", ()):
            return safeget(name)
        elif name in safeget('__prioritise__', ()):
            try:return safeget(name)
            except AttributeError as a:
                failed=True
                notes.append(f'Failed to find {name} in `self`: {a}')
        try:return getattr(safeget("_basemodule"), name)
        except AttributeError as e:
            notes.append(f'Failed to find {name} in `_basemodule`: {e}')
            try:
                errors=(failed, name in safeget("__raise__", ()),  name not in safeget("__typehintattrs__", ()))
                if any(errors):
                    if not errors[0]:
                        notes.append(f'{name} is either to be raised or not typehinted')
                    raise 
                return safeget(name)
            except Exception as e2: 
                tb = e.__traceback__
                filepath=Path(__file__)
                while tb is not None and filepath.samefile(tb.tb_frame.f_code.co_filename):
                    tb = tb.tb_next
                for note in notes:
                    e.add_note(note)
                raise e.with_traceback(tb)
    def __setattr__(self, name: str, value: Any) -> None:
        if name in safegetter(self,"__prioritise__", ()):
            object.__setattr__(self, name, value)
            if getattr(self._basemodule, name, missing) is missing:
                setattr(self._basemodule, name, value)
        elif name in safegetter(self,"__attrs__", ()):object.__setattr__(self, name, value)
        else:setattr(self._basemodule, name, value)
    def __dir__(self) -> set[str]:
        dirresults=set(super().__dir__()).union(dir(self._basemodule))
        dirresults.update(self.__attrs__)
        for hint in self.__typehintattrs__:
            if not hasattr(self._basemodule, hint):
                dirresults.add(hint)
        dirresults.update(self.__prioritise__)
        return dirresults
    def __eq__(self, value) -> bool:
        if value is None:
            return not self.isValid
        if isinstance(value, BaseModule):
            return value._basemodule==self._basemodule
        elif isinstance(value, ModuleType):
            return value.__file__==self._basemodule.__file__ or self._basemodule==value
        return self._basemodule.__eq__(value) 
    @classmethod
    def _tag(cls, func=None, *args,isAtrr=False, isHint=False, isPriority=False, isRaise=False, **kwargs):
        name=getattr(func, '__name__', str(func))
        if isAtrr:
            cls.__attrs__.add(name)
        if isHint:
            cls.__typehintattrs__.add(name)
        if isPriority:
            cls.__prioritise__.add(name)
        if isRaise:
            cls.__raise__.add(name)
    @property
    def isValid(self) -> bool:
        "A check on whether the module is the same as the empty one, if thats true, we failed to load and it is invalid"
        return self._basemodule is not EMPTYMODULE
    @staticmethod
    def __install__(*modulenames:str, trusted=False):

        if not modulenames:
            return {}
        import os
        from PyQt5.QtWidgets import QMessageBox, qApp


        _continue=os.environ.get("VIRTUAL_ENV") is not None

        if not _continue:
            if qApp:
                r=QMessageBox.warning(None,title='No virtual envinvironment', text="No virtual environment activated in the shell, Continue Anyway?", buttons=QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel, defaultButton=QMessageBox.StandardButton.Cancel)
                _continue= r == QMessageBox.StandardButton.Ok
            else:
                print("No virtual environment activated in the shell, and no app, quiting install")
                # TODO
                # Should we return None on failure? Or should we be more 'uniform' and return  an empty dictionary?. 
                # I doubt this would be used much any way. Besides the dict return only seems usefull to the languagetool, to determine which was installed successfully
                # But there are otherways to check, so it might be unneccessary
                # but language-check seems to require JAVA,and gives me the error 'ERROR: Failed to build 'language-check' when getting requirements to build wheel' when I attempt to install it, so what can we do about that?
                # I have Java on my windows so I think that not the problem but rather the part of the error where it says 'AttributeError: 'Constant' object has no attribute 's'' so I can't do anything about that
                return
        if qApp.instance() and(r:=QMessageBox.warning(None,qApp.tr('Trusted Install'),qApp.tr('Would you like to install as trusted source? Only use when normal install fails'),buttons=QMessageBox.StandardButton.Ok|QMessageBox.StandardButton.Cancel, defaultButton=QMessageBox.StandardButton.Cancel)):
            trusted=r == QMessageBox.StandardButton.Ok
        
        return InstallerWorker.startInstallation(modulenames, trusted=trusted).results   

def safegetter(obj,name:str, default:_A|object=missing)->Any|_A: 
    try:
        return object.__getattribute__(obj, name)
    except AttributeError:
        if default is missing:
            raise
        return default

class MODMD(BaseModule, hints=('markdown',), attrs=('subDict',)):
    """Stops typechecker from complaining that MD=None, despite isValid used to gaurd against this it when unavailable"""
    LibraryURL='https://pypi.org/project/Markdown/'
    LibraryName='markdown'
    
    class Extension:
        config: Mapping[str, list]
        def getConfigs(self) -> dict[str, Any]:... 
    subDict:dict[str, tuple[re.RegexFlag, str|Callable[[re.Match[str]], str]] | str| Callable[[re.Match[str]], str]]={
        r"```(?:\w+)?\n(.*?)```":(re.DOTALL,r"<pre><code>\1</code></pre>"),
        r"`([^`]+)`":(re.NOFLAG,r"<code>\1</code>",),
        r"^### (.+)$":(re.MULTILINE,r"<h3>\1</h3>"),
        r"^## (.+)$":(re.MULTILINE,r"<h2>\1</h2>"),
        r"^# (.+)$":(re.MULTILINE,r"<h1>\1</h1>"),
        r"\*\*(.+?)\*\*":(re.NOFLAG,r"<strong>\1</strong>"),
        r"__(.+?)__":r"<strong>\1</strong>",
        r"\*(.+?)\*":r"<em>\1</em>",
        r"_(.+?)_":r"<em>\1</em>",
        r"\[([^\]]+)\]\(([^)]+)\)":r'<a href="\2">\1</a>',
        r"(?:^- (.+)$\n?)+":(lambda m: f"<ul>{''.join(f'<li>{x}</li>\n' for x in re.findall(r'^- (.+)$', m.group(), re.MULTILINE))}</ul>"),
    }
    @classmethod
    def __install__(cls):
        return super().__install__('markdown')
    def __init__(self, name: str='markdown', doc: str | None = None, module=None) -> None:
        super().__init__(name, doc, basename='markdown',module=module)
    def markdown(self,text: str, *,extensions: Sequence['str | Any|MODMD.Extension'] | None = None,  extension_configs: Mapping[str, Mapping[str, Any]] | None = None,output_format: Literal['xhtml', 'html'] | None = None,tab_length: int | None = None)->str:
        """extensions is actually str|markdown.Extension, but no way to reference it without possibly resulting in an error or typechecker complaints\n
        In any case, I havent seen arguments besides text being used, so i doubt its necessary anyway\n
        # Original Doc\n
        Convert a markdown string to HTML and return HTML as a Unicode string.
        This is a shortcut function for [Markdown][markdown.Markdown] class to cover the most basic use case. It initializes an instance of [Markdown][markdown.Markdown], loads the necessary extensions and runs the parser on the given text.

        Arguments
        text
        Markdown formatted text as Unicode or ASCII string.

        Keyword arguments:

        **kwargs: Any arguments accepted by the Markdown class.

        Returns
        out
        A string in the specified output format.

        !!! warning

        The Python-Markdown library does not sanitize its HTML output.
        If you are processing Markdown input from an untrusted source, it is your
        responsibility to ensure that it is properly sanitized. For more
        information see Sanitizing HTML Output."""
        if self.isValid:
            return self._basemodule.markdown(text, extensions=extensions, extension_configs=extension_configs, output_format=output_format, tab_length=tab_length)
        md=str(text)
        flag=re.NOFLAG
        for pattern, value in self.subDict.items():
            if isinstance(value, tuple):
                flag, repl =value
            else:
                repl = value
            md = re.sub(pattern, repl, md, flags=flag)
        lines = md.splitlines()
        result = []
        for line in lines:
            if not line.strip():
                continue
            if line.startswith(("<h1>", "<h2>", "<h3>", "<ul>", "</ul>", "<pre>")):
                result.append(line)
            else:
                result.append(f"<p>{line}</p>")
        return "\n".join(result)
class ENCHANT(BaseModule, hints=('get_default_language','dict_exists', 'list_dicts')):
    LibraryURL="https://pypi.org/project/pyenchant/"
    LibraryName='PyEnchant'
    def list_dicts(self)->list[tuple[str, 'ENCHANT.ProviderDesc']]:
        """This method returns a list of dictionaries available to the broker. 
        \nEach entry in the list is a two-tuple of the form:            (tag,provider)"""
        return []
    class ProviderDesc:
        def __init__(self, name:str, desc:str, file:str):
            self.name = name
            self.desc = desc
            self.file = file
    class DictWithPWL(dict):
        """Dictionary with separately-managed personal word list.
        .. note::
            As of version 1.4.0, enchant manages a per-user pwl and
            exclude list.  This class is now only needed if you want
            to explicitly maintain a separate word list in addition to
            the default one.

        This class behaves as the standard Dict class, but also manages a
        personal word list stored in a separate file.  The file must be
        specified at creation time by the 'pwl' argument to the constructor.
        Words added to the dictionary are automatically appended to the pwl file.

        A personal exclude list can also be managed, by passing another filename
        to the constructor in the optional 'pel' argument.  If this is not given,
        requests to exclude words are ignored.

        If either 'pwl' or 'pel' are None, an in-memory word list is used.
        This will prevent calls to add() and remove() from affecting the user's
        default word lists.

        The Dict object managing the PWL is available as the 'pwl' attribute.
        The Dict object managing the PEL is available as the 'pel' attribute.

        To create a DictWithPWL from the user's default language, use None
        as the 'tag' argument.
        """

        _DOC_ERRORS = ["pel", "pel", "PEL", "pel"]

        def __init__(self, tag, pwl=None, pel=None, broker=None):...
        def check(self, word)->bool:
            """Check spelling of a word.

            This method takes a word in the dictionary language and returns
            True if it is correctly spelled, and false otherwise.  It checks
            both the dictionary and the personal word list.
            """
            ...
        def suggest(self, word)->list[str]:
            """Suggest possible spellings for a word.

            This method tries to guess the correct spelling for a given
            word, returning the possibilities in a list.
            """
            ...
        def add(self, word):
            """Add a word to the associated personal word list.

            This method adds the given word to the personal word list, and
            automatically saves the list to disk.
            """
            ...
        def remove(self, word):
            """Add a word to the associated exclude list."""
            ...
        def is_added(self, word)->bool:
            """Check whether a word is in the personal word list."""
            ...
    @classmethod
    def __install__(cls):
        return super().__install__('pyenchant')
    def __init__(self, name: str='enchant', doc: str | None = None, module: ModuleType | None = None) -> None:
        super().__init__(name, doc, 'enchant', module)
    @staticmethod
    def dict_exists(tag)->bool:
        """Check availability of a dictionary.
        This method checks whether there is a dictionary available for
        the language specified by 'tag'.  It returns True if a dictionary
        is available, and False otherwise.
        """
        return False
    @staticmethod
    def get_default_language(default:_A=None)->str|_A:
        """Determine the user's default language, if possible.

        This function uses the 'locale' module to try to determine
        the user's preferred language.  The return value is as
        follows:

            * if a locale is available for the LC_MESSAGES category,
            that language is used
            * if a default locale is available, that language is used
            * if the keyword argument <default> is given, it is used
            * if nothing else works, None is returned

        Note that determining the user's language is in general only
        possible if they have set the necessary environment variables
        on their system.
        """
        try:
            from locale import getdefaultlocale, getlocale
            for m in (getlocale,getdefaultlocale):
                tag=m()[0]
                if tag is not None:
                    return tag
            return default
        except Exception:
            return default
class CHECKER(BaseModule, attrs=('resource','cachedresource')):
    LibraryURL="https://pyspellchecker.readthedocs.io/en/latest/"
    LibraryName="pyspellchecker"
    def __init__(self, name: str='pyspellchecker', doc: str | None = None, module: ModuleType | None = None) -> None:
        super().__init__(name, doc, 'spellchecker', module)
        self.cachedresource=self.resource()
    def resource(self)->dict[str, Path]:
        r={}
        try:
            path=getattr(self, '__path__', None)
            if path is not None:
                r= {p.name:p for p in Path(path[0], "resources").glob("*.json.gz")}
        except Exception:
            if hasattr(self, 'cachedresource'):
                r=self.cachedresource.copy()
        finally:
            self.cachedresource=r.copy()
        return r
            
    @classmethod
    def __install__(cls):
        return super().__install__('pyspellchecker')
class SYMSPELLPY(BaseModule):
    LibraryRequirement='>= '+SYMSPELLPY_MIN_VERSION
    LibraryURL="https://github.com/mammothb/symspellpy"
    LibraryName='symspellpy'
    class SymSpell:
        def __init__(self, max_dictionary_edit_distance: int = 2, prefix_length: int = 7, count_threshold: int = 1, distance_comparer = None,) -> None:
            pass
        def load_pickle(self, data: bytes | Path|str, compressed: bool = True, from_bytes: bool = False,) -> bool:...
        def create_dictionary(self, corpus: Path | str | IO[str], encoding: str | None = None, errors: str | None = None,) -> bool:...
        def create_dictionary_entry(self, key: str, count: int) -> bool:...
        def save_pickle(self, filename: str|Path | None = None, compressed: bool = True, to_bytes: bool = False,) -> bytes | None:...
        def lookup(self, phrase: str, verbosity, max_edit_distance: int | None = None, include_unknown: bool = False, ignore_token: re.Pattern[str] | None = None, transfer_casing: bool = False,) -> list:...
        def lookup_compound(self, phrase: str, max_edit_distance: int, ignore_non_words: bool = False, transfer_casing: bool = False, split_by_space: bool = False, ignore_term_with_digits: bool = False,) -> list:...
        def delete_dictionary_entry(self, key: str) -> bool:...
    def __init__(self, name: str='symspellpy', doc: str | None = None,  module: ModuleType | None = None) -> None:
        super().__init__(name, doc, '', module)
    @classmethod
    def __install__(cls):
        return super().__install__(f'symspellpy>={SYMSPELLPY_MIN_VERSION}')
class LANGUAGETOOL(BaseModule, attrs=('LibraryURL','_java','maketool','getTool','tools','use_language_check','local_language', 'get_match_message', 'match_errorLength', 'match_ruleIssueType', 'match_message'), hints=('get_languages',)):
    _java:bool|None=None
    LibraryName='LanguageTool'
    tools:set['LANGUAGETOOL.LanguageTool']=set()
    def maketool(self, lang:str|None=None,*args, **kwargs):
        'Add the created tool to LANGUAGETOOL.tools, so on closing, we can call tool.close to shut down servers'
        if self.isValid:
            tool=self.LanguageTool(*args,language=lang, **kwargs)
            self.tools.add(tool)
            return tool
    
    class LanguageTool:
        def __init__(self,
            language: Optional[str] = None,
            mother_tongue: Optional[str] = None,
            remote_server: Optional[str] = None,
            new_spellings: Optional[list[str]] = None,
            new_spellings_persist: bool = True,
            host: Optional[str] = None,
            config: Optional[dict[str, Any]] = None,
            language_tool_download_version: str = ...,
            proxies: Optional[dict[str, str]] = None,
        ) -> None:...
        def _get_languages(self)->set[str]:...
        def close(self):
            """Closes the server and performs necessary cleanup operations.
            This method performs the following actions:

            Checks if the server is alive, not remote and terminates it if necessary.
            If new spellings are not set to persist and there are new spellings, it unregisters the spellings and clears the list of new spellings."""
            ...
    class Match:
        """
        Represents a match object that contains information about a language rule violation.

        :param attrib: A dictionary containing various attributes for the match.
        :type attrib: Dict[str, Any]
        :param text: The original text in which the error occurred (the whole text, not just the context).
        :type text: str

        """

        PREVIOUS_MATCHES_TEXT: Optional[str] = None
        """The text of the previous match object."""

        FOUR_BYTES_POSITIONS: Optional[list[int]] = None
        """The positions of 4-byte encoded characters in the text, registered by the previous match object
        (kept for optimization purposes if the text is the same)."""

        rule_id: str
        """The ID of the rule that was violated."""
        msg:str
        message: str
        """The message describing the error."""

        replacements: list[str]
        """A list of suggested replacements for the error."""

        offset_in_context: int
        """The offset of the error in the context."""

        context: str
        """The context in which the error occurred."""

        offset: int
        """The offset of the error."""
        errorlength:int
        error_length: int
        """The length of the error."""

        category: str
        """The category of the rule that was violated."""
        locqualityissuetype: str
        rule_issue_type: str
        """The issue type of the rule that was violated."""
        
        def __init__(self, attrib: dict[str, Any], text: str) -> None:...
        @property
        def matched_text(self) -> str:...
    @property
    @tag(isAtrr=True)
    def LibraryURL(self):
        if self.use_language_check:
            return "https://pypi.org/project/language-check/"
        return "https://pypi.org/project/language-tool-python/"
    def __init__(self, name: str='languagetool', doc: str | None = None, module: ModuleType | None = None) -> None:
        super().__init__(name, doc, ('language_tool_python','language_check'), module)
    @classmethod
    def __install__(cls):
        if cls._java is None:
            cls._java=subprocess.Popen('java -version', stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()==0
        if not cls._java:
            print('No Java detected, please add it to path or install it first')
            return
        return super().__install__('language_tool_python','language-check')

    def getTool(self,LanguageToolDictionary)->'LANGUAGETOOL.LanguageTool|None':
        if self.isValid and  LanguageToolDictionary._tool == None:
            try:
                LanguageToolDictionary._tool = self.maketool()
            except Exception as e:
                return None
        return LanguageToolDictionary._tool

    @property
    def isValid(self):# -> bool:
        """A check on whether the module is the same as the empty one, if thats true, we failed to load and it is invalid. Also check if Java is installed\n
        returns False if we have no _basemodule, 0 if we have no Java, 1 if we are language_check and 2 if language_tool_python"""
        if not super().isValid:
            return False
        if self._java is None:
            self._java=subprocess.Popen('java -version', stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()==0
        if not self._java:
            return 0        
        if getattr(self._basemodule, '__name__', '') =='language_check':
            return 1
        return 2
    @property
    def use_language_check(self)->bool:
        return self.isValid==1
    def get_match_message(self,match:'LANGUAGETOOL.Match'):
        if self.use_language_check:
            return match.msg
        return match.message
    def get_languages(self, tool:'LANGUAGETOOL.LanguageTool|None'=None)->Iterable[str]:
        if self.isValid:
            if self.use_language_check:
                return self._basemodule.get_languages()
            elif tool is not None or (tool:=self.maketool()):
                return tool._get_languages()
            return [self.local_language]#we are sure we  are valid, so we can infer the same is true for our 'local_language'
        return ()
    @property
    def local_language(self)->str:
        'Attempts to use language_tool_python or language_check to get the locale languege, failing that, use the default one from Enchant'
        if self.isValid:
            if self.use_language_check:
                return self._basemodule.get_locale_language()
            return self._basemodule.utils.get_locale_language()
        return ENCHANT.get_default_language() or 'en'

    def match_errorLength(self,match:'LANGUAGETOOL.Match'):
        if self.use_language_check:
            return match.errorlength
        return match.error_length
    
    def match_ruleIssueType(self,match:'LANGUAGETOOL.Match'):
        if self.use_language_check:
            return match.locqualityissuetype
        return match.rule_issue_type

    def match_message(self,match:'LANGUAGETOOL.Match'):
        return self.get_match_message(match)

@register
def onExit():
    'Sometimes on startup, languagetool complains we left servers open, this is to get around that by making sure it closes where possible'
    try:
        from logging import getLogger
    except Exception:
        return
    logger=getLogger('LanguageTool')
    for tool in LANGUAGETOOL.tools:
        try:
            tool.close()
        except Exception as e:
            logger.warning(e, exc_info=True)

class LXMLETREE(BaseModule, hints=('tostring','LXML_VERSION', 'LIBXML_VERSION', 'LIBXML_COMPILED_VERSION', 'LIBXSLT_VERSION', 'LIBXSLT_COMPILED_VERSION')):
    LibraryURL='https://pypi.org/project/Markdown/'
    LibraryName='markdown'
    LIBXSLT_COMPILED_VERSION:tuple[int, ...]=()#
    LIBXSLT_VERSION:tuple[int, ...]=()
    __version__:str

    from xml.etree.ElementTree import XMLParser,ElementTree, Element, XML
    def parse(self,source, parser: XMLParser[Any] | None = None, baseurl:str|bytes='') -> 'LXMLETREE.ElementTree[Element[str]]':

        """Parse XML document into element tree.

        source is a filename or file object containing XML data,
        parser is an optional parser instance defaulting to XMLParser.

        Return an ElementTree instance."""
        ...
    # TODO GENERAL
    # XMLParser,ElementTree,parse, fromstring
    # Seems the only things used are the following:
    # tostring ✓, fromstring ✓,XMLParser,ElementTree,parse,  Element, SubElement, XML
    # Native xml can do all of them
    # TODO lxml specific stuff to get/fake from xml, currently we just return empty tuples, should we populate them with negatives/None to show they dont exist?
    # LIBXML_COMPILED_VERSION
    # LIBXSLT_VERSION
    # LIBXSLT_COMPILED_VERSION
    
    def __init__(self, name: str='etree', doc: str | None = None,module: ModuleType | None = None) -> None:
        super().__init__(name, doc, ('lxml.etree','xml.etree.ElementTree'), module)
        self.__version__=getVersion(self._basemodule)
        from xml.etree.ElementTree import SubElement
    @tag(isHint=True)
    def SubElement(self,parent, tag, attrib={}, **extra)->'LXMLETREE.Element[str]':...
    @classmethod
    def __install__(cls):
        from PyQt5.QtWidgets import qApp, QMessageBox
        warning=QMessageBox.warning if qApp else None
        if warning is not None and  warning(None, 'lxml installation', 'Are you sure you want to install lxml? It is faster in some cases but the buitin xml has most of its functions.')!=QMessageBox.StandardButton.Ok:
            return super().__install__()
        r= super().__install__('lxml')
        if r is not None and warning is not None:
            w=warning(None, 'lxml stubs', 'Since you have installed lxml, would you also like to install its stubs? Unneccesarry for those who arent developing anything')
            if w==QMessageBox.StandardButton.Ok:
                r={**r,**(super().__install__('lxml-stubs') or {})}
        return r
    @property
    def LIBXML_VERSION(self):
        return tuple(map(int,self.__version__.split('.')))
    @property
    def LIBXML_COMPILED_VERSION(self):
        return self.LIBXML_VERSION
    @property
    def LXML_VERSION(self):
        return tuple(map(int,self.__version__.split('.')))
    @overload
    def tostring(self,source:Any='', encoding: Literal['ascii'] = 'ascii', *args, **kwargs) -> bytes: ...
    @overload
    def tostring(self,source:Any='', encoding: Literal["unicode"]="unicode", *args, **kwargs) -> str: ...
    @overload
    def tostring(self,source:Any='', encoding: str|Literal['ascii'] = 'ascii', *args, **kwargs) -> bytes: ...
    @tag(isHint=True)
    def tostring(self,source:Any='', encoding='ascii',*args, **kwargs):
        if not isinstance(source, str):
            source=str(source, encoding=encoding,errors='ignore')
        if encoding =='unicode':
            return source
        return source.encode(encoding=encoding,errors='ignore')
    def fromstring(self,text: str, parser: 'LXMLETREE.XMLParser| None' = None) -> 'LXMLETREE.Element[str]':...
    @tag(isAtrr=True)
    def hugeparser(self):
        if self.isValid:
            if self._basemodule.__name__.startswith('xml'):
                #This is why in general we prefer lxml, it dooesnt store everything in memory unlike xml, and we load a lot of stuff
                return self.XMLParser()
            return self.XMLParser(huge_tree=True) # pyright: ignore[reportCallIssue]
        raise AttributeError
class YAML(BaseModule, attrs=('load','MYLoader', 'save'), hints=('safe_load',)):
    # I no longer remember why i made this so I'm just leaving it there
    LibraryURL='https://pypi.org/project/PyYAML/'
    LibraryName='Yaml'
    SafeLoader:type
    def __init__(self, name: str='yaml', doc: str | None = None) -> None:
        super().__init__(name, doc, 'yaml')
        if self.isValid:
            MYLoader=type('MYLoader',(self.SafeLoader,),{})
            MYLoader.add_constructor("tag:yaml.org,2002:null", lambda *args:'')
        else:
            MYLoader=type('MYLoader',(), {})
        self.MYLoader=MYLoader
    @classmethod
    def __install__(cls):
        return super().__install__('pyyaml')
    @tag(isAtrr=True)
    def load(self, stream, loader=None, useload=True)->dict:
        if self.isValid and useload:
            return self._basemodule.load(stream, loader or self.MYLoader)
        return self.safe_load(stream)
    def safe_load(self, stream)->Any|dict:
        def LiteralValue(value):
            import ast 
            try:
                return ast.literal_eval(value)
            except Exception:
                return value
        if not isinstance(stream, str):
            stream=str(stream)
        result = {}
        for line in stream.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                result[key] = None
            else:
                result[key]=LiteralValue(value)
        return result
    @tag(isAtrr=True)
    def save(self, data, filename="file.yaml"):
        with open(filename, "w") as f:
            try:
                if self.isValid:
                    self.safe_dump(data,f,sort_keys=False)
                else:
                    f.write(str(data))
                return True
            except Exception:
                return False

if not TYPE_CHECKING:
    try:
        try:
            from packaging.version import Version # pyright: ignore[reportMissingImports]
        except ImportError:
            class Version(str):
                def __lt__(self, value: str) -> bool:
                    if not isinstance(value, str):
                        return NotImplemented
                    def toInt(s):
                        try:
                            return int(s)
                        except ValueError:
                            return -1
                    self_parts = tuple(map(toInt,self.split('.')))
                    other_parts = tuple(map(toInt,value.split('.')))
                    for v, other in zip(self_parts, other_parts):
                        if v != other:
                            return v < other
                    return len(self_parts) < len(other_parts)
                def __gt__(self, value: str) -> bool:
                    return not self.__eq__(value) and not self.__lt__(value)
        import symspellpy as symspellpymod
        v=getVersion(symspellpymod)
        if not v or Version(getVersion(symspellpymod)) < Version(SYMSPELLPY_MIN_VERSION):
            symspellpymod=None
    except ImportError:
        symspellpymod = None
enchant=ENCHANT()
MD=MODMD('MD')
markdown=MODMD(name='markdown')
pyspellchecker=CHECKER()
languagetool=LANGUAGETOOL()
use_language_check=languagetool.use_language_check
symspellpy=SYMSPELLPY(module=symspellpymod)
etree=LXMLETREE()
ET=LXMLETREE()
yaml=YAML()

