#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
import subprocess

class basicExporter():
    
    def __init__(self):
        pass
    
    def runT2T(self, text, target="html"):
        
        cmdl = ['txt2tags', '-t', target, '--enc=utf-8', '--no-headers', '-o', '-', '-']
        
        cmd = subprocess.Popen(('echo', text), stdout=subprocess.PIPE)
        try:
            output = subprocess.check_output(cmdl, stdin=cmd.stdout, stderr=subprocess.STDOUT) # , cwd="/tmp"
        except subprocess.CalledProcessError as e:
            print("Error!")
            return text
        cmd.wait()
        
        return output.decode("utf-8")
