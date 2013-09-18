# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import re
import sys
import logging
import subprocess

import init
init.init()

import colors
import util

qa_dir = os.path.dirname(os.path.abspath(__file__))

def get_tests():
    tests = []
    for f in os.listdir (qa_dir):
        if re.match (r'^\d{3}-.+\.py$', f):
            tests.append (f)

    tests.sort()
    return tests

def main():
    # Argument parsing
    ns = util.do_argparse()
    if ns.debug:
        logging.basicConfig (level = logging.DEBUG)

    # Execute tests
    for f in get_tests():
        print (colors.green(f))
        fp = os.path.join (qa_dir, f)
        logging.info ('Executing: %s %s'%(sys.executable, fp))
        subprocess.check_call([sys.executable, fp] + sys.argv[1:])


if __name__ == '__main__':
    main()
