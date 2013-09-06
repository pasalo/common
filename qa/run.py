# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import re
import sys
import subprocess

import util

qa_dir = os.path.dirname(__file__) or '.'

def get_tests():
    tests = []
    for f in os.listdir (qa_dir):
        if re.match (r'^\d{3}-.+\.py$', f):
            tests.append (f)

    tests.sort()
    return tests


def main():
    for f in get_tests():
        print (util.green(f))
        fp = os.path.join (qa_dir, f)
        subprocess.check_call([sys.executable, fp])

if __name__ == '__main__':
    main()
