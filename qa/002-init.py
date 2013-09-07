import os
import sys
import util
import logging
import threading
import multiprocessing

# Globals
TMP1 = '/tmp/pasalo-QA-1'
TMP2 = '/tmp/pasalo-QA-2'

HOST1_PORT = 44300

# Create keys
util.pasalo_init_paths ([TMP1, TMP2])

# Test directory structure
for path in (TMP1, TMP2):
    for f in ('gpg', 'https', 'config.json'):
        fp = os.path.join (path, f)
        assert os.path.exists (fp), "Path should exist %s"%(fp)

# Get keys
key1 = util.popen_py ('df-get-key.py', '--confdir=%s'%(TMP1)).read()
key2 = util.popen_py ('df-get-key.py', '--confdir=%s'%(TMP2)).read()

assert key1 != key2
assert len(key1) == len(key2)
assert '-----BEGIN PGP PUBLIC KEY BLOCK-----' in key1
assert '-----BEGIN PGP PUBLIC KEY BLOCK-----' in key2
assert '-----END PGP PUBLIC KEY BLOCK-----' in key1
assert '-----END PGP PUBLIC KEY BLOCK-----' in key2

# Cross-import keys
key1_fp = os.path.join(TMP1,'key')
key2_fp = os.path.join(TMP2,'key')
open(key1_fp, 'w+').write(key1)
open(key2_fp, 'w+').write(key2)

util.system_py ('df-links.py', 'add --confdir=%s --cert=%s --name=host2'%(TMP1, key2_fp))
util.system_py ('df-links.py', 'add --confdir=%s --cert=%s --name=host1 --url=https://localhost:%s/'%(TMP2, key1_fp, HOST1_PORT))

for d in [TMP1, TMP2]:
    host_keys = util.popen_py ('df-get-key.py', '--confdir=%s --list'%(d)).read()
    assert host_keys.count('pub id=') == 2

# Launch server
def run_server(p_srv):
    p_srv.communicate()

p_srv = util.Popen_py ('main.py', ['server', '--confdir=%s'%(TMP1), '--port=%d'%(HOST1_PORT), '--bind=localhost'], stdout=sys.stdout, stderr=sys.stderr)
p = multiprocessing.Process (target=run_server, args=[p_srv])
p.start()

timeout = util.wait_for_port('localhost', HOST1_PORT)
assert not timeout

# Ping
ping1 = util.popen_py ('df-ping.py', '--confdir=%s host1'%(TMP2)).read()
print ping1
assert ping1.count('time=') == 5

# Clean up
p_srv.terminate()
p.terminate()
