import os
import sys
import time
import socket
import hashlib
import argparse
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
def pasalo_init_path (path, **args):
    KEYS_TO_PASS = ['downloads', 'public_url']

    cmd = '%s/df-init.py --confdir=%s'%(src_dir, path)

    for key in KEYS_TO_PASS:
        if key in args:
            cmd += ' --%s=%s'%(key, args[key])

    system_py (cmd)


# System
#
def wait_for_port (host, port):
    for n in range(60):
        try:
            s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            with contextlib.closing(s):
                s.connect ((host, port))
        except Exception:
            time.sleep(1)
        else:
            break
    else:
        return 1

# MD5
#
def md5_file (fullpath):
    m = hashlib.md5()
    with open(fullpath, 'r') as f:
        while True:
            cont = f.read(1024 * 1024)
            if not cont:
                break
            m.update (cont)
    return m.hexdigest()


# CLI
#
def do_argparse():
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument ('--debug',    action="store_true", help="Enable debugging")
    parser.add_argument ('--new-keys', action="store_true", help="Do not reuse keys in case they're available")
    return parser.parse_args()
