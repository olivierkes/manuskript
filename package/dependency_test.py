import os
import sys

realpath = os.path.realpath(__file__)

sys.path.insert(1, os.path.join(os.path.dirname(realpath), '..'))

from manuskript import main
