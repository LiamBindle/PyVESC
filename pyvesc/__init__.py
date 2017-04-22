import sys
if sys.version_info < (3,3):
    raise SystemExit("Invalid Python version. PyVESC requires Python 3.3 or greater.")

from pyvesc.interface import *
from pyvesc.messages import *
