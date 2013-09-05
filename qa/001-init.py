import os
import conf
import util
import logging

v = vars(conf)
v.update (vars(util))

os.system ('rm -rf %(TMP1)s %(TMP2)s' %(v))
util.run_py ('%(src_dir)s/df-init.py --confdir=%(TMP1)s' %(v))
util.run_py ('%(src_dir)s/df-init.py --confdir=%(TMP2)s' %(v))


for path in (conf.TMP1, conf.TMP2):
    for f in ('gpg', 'https', 'config.json'):
        fp = os.path.join (path, f)
        assert os.path.exists (fp), "Path should exist %s"%(fp)
