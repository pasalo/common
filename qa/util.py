import os
import sys
import time
import socket
import subprocess
import contextlib


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

def src_py (py_name):
    return os.path.join (src_dir, py_name)

def system_py (name, args=''):
    return os.system ('%s %s %s' %(sys.executable, src_py(name), args))

def popen_py (name, args=''):
    return os.popen ('%s %s %s' %(sys.executable, src_py(name), args), 'r')

def Popen_py (name, cmd_args, **args):
    cmd = [sys.executable, src_py(name)] + cmd_args
    return subprocess.Popen(cmd, **args)


#
#
def pasalo_init_paths (paths, remove=True):
    for path in paths:
        if remove:
            os.system ('rm -rf %s'%(path))

        system_py ('%s/df-init.py --confdir=%s'%(src_dir, path))

# System
#
def wait_for_port (host, port):
    for n in range(60):
        try:
            s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            with contextlib.closing(s):
                s.connect ((host, port))
        except Exception:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
        else:
            break
    else:
        return 1
