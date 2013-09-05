import os
import sys

# Execution
#
def run_py (cmd):
    os.system ('%s %s' %(sys.executable, cmd))


# Colors
#
ESC   = chr(27) + '['
RESET = '%s0m' % (ESC)

def green (s):
    return ESC + '0;32m' + s + RESET
def red (s):
    return ESC + '0;31m' + s + RESET
def yellow (s):
    return ESC + '1;33m' + s + RESET
def blue (s):
    return ESC + '0;34m' + s + RESET

# Paths
#
qa_dir  = os.path.dirname(__file__)
src_dir = os.path.normpath (os.path.join (qa_dir + '/..'))
