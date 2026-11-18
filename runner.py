# from PyQt5.uic import compileUi
# with open(r"G:\My Drive\manuskript-develop\manuskript-develop\manuskript\ui\mainWindow.py", 'w') as f:
#     compileUi(r"G:\My Drive\manuskript-develop\manuskript-develop\manuskript\ui\mainWindow.ui", f)

from manuskript.main import run, process_commandline, sys, prepare, setup_signal_handlers, launch
from typing import Generic, TypeVar, Literal, overload, Any, TYPE_CHECKING
from PyQt5.QtWidgets import QApplication, QMainWindow
if TYPE_CHECKING:
    from manuskript.mainWindow import MainWindow
else:
    MainWindow=QMainWindow
from manuskript import inspectCall
MANUSKRIPTRETURNS=TypeVar('MANUSKRIPTRETURNS', bound=Literal[-1,0, 1], default=Literal[-1])

class TempManuskript(Generic[MANUSKRIPTRETURNS]):
    """For testing purposes, set mode to 1 to launch app after our block, 0 does nothing, -1 exits the app"""
    class Returns:
        appWindow=-1
        manuContext=0
        appWindowNamespace=1
    class Mode:
        Null=0
        Launch=1
        Quit=-1
    

    def __init__(self, returns:MANUSKRIPTRETURNS=-1,mode:Literal[-1,0, 1]|TempManuskript.Mode=1) -> None:
        self.mode:Literal[-1,0, 1]=mode # pyright: ignore[reportAttributeAccessIssue]
        self.returns=returns
    @staticmethod
    def getAPP():
        """
        Taken from manuskript.main.run(), just without launching
        
        @original documentation
        Run separates prepare and launch for two reasons:
        1. I've read somewhere it helps with potential segfault (see comment below)
        2. So that prepare can be used in tests, without running the whole thing
        @param delete: whether or not to clean app immediatley on close
        """
        from manuskript.main import process_commandline, prepare, setup_signal_handlers
        import manuskript.logging
        # Parse command-line arguments.
        arguments = process_commandline(sys.argv[1:])
        # Initialize logging. (Does not include Qt integration yet.)
        manuskript.logging.setUp(console_level=arguments.verbose)
        # Need to return and keep `app` otherwise it gets deleted.
        app, MW = prepare(arguments)
        setup_signal_handlers(MW)
        return app, MW, arguments
    @overload
    def __enter__(self: "TempManuskript[Literal[-1]]") -> tuple[QApplication,MainWindow]: ...
    @overload
    def __enter__(self: "TempManuskript[Literal[0]]") -> "TempManuskript[Any]": ...
    @overload
    def __enter__(self: "TempManuskript[Literal[1]]") -> tuple[QApplication,MainWindow, Any]: ...
    @overload
    def __enter__(self: "TempManuskript[Any]") -> tuple[QApplication,MainWindow]: ...
    def __enter__(self): # pyright: ignore[reportInconsistentOverload]
        self.app,self.MW, self.args=self.getAPP()
        self.MW.show()
        match self.returns:
            case self.Returns.manuContext:
                return self
            case self.Returns.appWindowNamespace:
                return self.app,self.MW, self.args
            case self.Returns.appWindow:
                return self.app,self.MW
            case other:
                return self.app,self.MW
        return self.app, self.MW
    def launch(self):
        launch(self.args, self.app, self.MW)
    def __exit__(self, exc_type, exc_value, traceback):
        print(f'exiting with {self.mode}')
        from manuskript.main import launch
        match self.mode:
            case self.Mode.Null:
                return
            case self.Mode.Launch:
                self.launch()
            case self.Mode.Quit:
                self.app.quit()
            case other:
                print(f'Unkown mode: {other}')
RUNTYPE=3#0-run(), 1-RunTemp(), 3- Run the block the user wrote in
def RunTemp(mode:TempManuskript.Mode|Literal[-1,0, 1]=-1):
    Temp=TempManuskript(mode=mode)
    with Temp as (app, MW):
        mdl=MW.mdlPlots
        if mdl.rowCount():
            print(mdl.rowPlot(0))
        # def addChar(name, desc=''):
        #     from manuskript.enums import Character as C
        #     c=mdl.addCharacter(name=name)
        #     if desc:
        #         mdl.setData(c.index(C.notes), desc)
        # def addChars(chars:str):
        #     for line in chars.splitlines():
        #         char,_, desc=line.strip().partition(',')
        #         char=char.strip()
        #         desc=desc.strip()
        #         addChar(char, desc)
        
    
if __name__=='__main__':
    match RUNTYPE:
        case 0:
            run()
        case 1:
            RunTemp()
        case other:
            from manuskript.ui.css_style import getminorSS
            print(getminorSS('toolTipSS'))


