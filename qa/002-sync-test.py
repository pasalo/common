# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import sys
import util
import shutil
import hashlib
import logging
import threading
import multiprocessing

import init
init.init()

import keys
import colors

# Globals
TMP1 = '/tmp/pasalo-QA-1'
TMP2 = '/tmp/pasalo-QA-2'
DWN1 = '/tmp/pasalo-down-1'
DWN2 = '/tmp/pasalo-down-2'

HOST1_PORT = 44300
HOST1_URL  = 'https://localhost:%s' %(HOST1_PORT)

# Argument parsing
ns = util.do_argparse()

# Preparison
print (colors.yellow(" * Remoing %s" %(', '.join([TMP1, TMP2, DWN1, DWN2]))))

for d in (TMP1, TMP2, DWN1, DWN2):
    logging.info ("Removing %s"%(d))
    shutil.rmtree (d, ignore_errors=True)

# Create keys
keys.init (ns.new_keys)
keys.create ('1', TMP1, DWN1, HOST1_URL)
keys.create ('2', TMP2, DWN2)

# Test directory structure
for path in (TMP1, TMP2):
    for f in ('gpg', 'https', 'config.json'):
        fp = os.path.join (path, f)
        assert os.path.exists (fp), "Path should exist %s"%(fp)

# Get keys
print (colors.yellow(" * Checking keys"))

key1 = util.popen_py ('df-get-key.py', '--confdir=%s'%(TMP1)).read()
key2 = util.popen_py ('df-get-key.py', '--confdir=%s'%(TMP2)).read()

assert key1 != key2
assert HOST1_URL in key1
assert not HOST1_URL in key2
assert '-----BEGIN PGP PUBLIC KEY BLOCK-----' in key1
assert '-----BEGIN PGP PUBLIC KEY BLOCK-----' in key2
assert '-----END PGP PUBLIC KEY BLOCK-----' in key1
assert '-----END PGP PUBLIC KEY BLOCK-----' in key2

# Cross-import keys
key1_fp = os.path.join(TMP1,'key')
key2_fp = os.path.join(TMP2,'key')
open(key1_fp, 'w+').write(key1)
open(key2_fp, 'w+').write(key2)

print (colors.yellow(" * Cross-importing keys"))

util.system_py ('df-links.py', 'add --confdir=%s --cert=%s --name=host2'%(TMP1, key2_fp))
util.system_py ('df-links.py', 'add --confdir=%s --cert=%s --name=host1'%(TMP2, key1_fp))

for d in [TMP1, TMP2]:
    host_keys = util.popen_py ('df-get-key.py', '--confdir=%s --list'%(d)).read()
    assert host_keys.count('pub id=') == 2

# Launch server
def run_server(p_srv):
    p_srv.communicate()

print (colors.yellow(" * Launching server"))
p_srv = util.Popen_py ('main.py', ['server', '--confdir=%s'%(TMP1), '--port=%d'%(HOST1_PORT), '--bind=localhost', '--downloads=%s'%(DWN1)], stdout=sys.stdout, stderr=sys.stderr)
p = multiprocessing.Process (target=run_server, args=[p_srv])
p.start()

print (colors.yellow(" * Waiting for server to get ready"))
timeout = util.wait_for_port('localhost', HOST1_PORT)
assert not timeout

# Ping
print (colors.yellow(" * Pinging server"))

ping1 = util.popen_py ('df-ping.py', '--confdir=%s host1'%(TMP2)).read()
print ping1
assert ping1.count('time=') == 5

# Check channels
print (colors.yellow(" * Channels show up"))

channels = ['channel1', 'new.channel', 'yet.another.one']
for channel in channels:
    fp = os.path.join (DWN1, channel)
    os.makedirs (fp, 0700)

chan_list = util.popen_py ('main.py', 'channels --confdir=%s --name=host1'%(TMP2)).read()
print chan_list
for channel in channels:
    assert channel in chan_list

# File in a channel
print (colors.yellow(" * Channels contain the right files"))

CONTENT_NAME = "Example file.txt"
CONTENT = "Visit http://pasalo.org/"

hasher = hashlib.md5()
hasher.update(CONTENT)
md5 = hasher.hexdigest()

open (os.path.join (DWN1, channels[1], CONTENT_NAME), 'w+').write(CONTENT)

file_list = util.popen_py ('main.py', 'ls --confdir=%s --channels=%s --name=host1'%(TMP2, channels[1])).read()
print file_list
assert md5 in file_list
assert CONTENT_NAME in file_list

# Subscribe channels
print (colors.yellow(" * Synchronization"))

util.system_py ('df-links.py', 'subscribe --confdir=%s --channel=%s --name=host1'%(TMP2, channels[1]))
util.system_py ('main.py', 'sync --confdir=%s --name=host1 --downloads=%s'%(TMP2, DWN2))

f1 = os.path.join (DWN1, channels[1], CONTENT_NAME)
f2 = os.path.join (DWN1, channels[1], CONTENT_NAME)
f_md5 = util.md5_file(f1)

assert os.path.getsize(f1) == os.path.getsize(f2)
assert open(f1,'r').read() == open(f2,'r').read()
assert f_md5 == util.md5_file(f2)

print (colors.yellow(" * %s downloaded correctly: %s" %(CONTENT_NAME, f_md5)))


# Clean up
p_srv.terminate()
p.terminate()
