# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import re
import sys
import logging
import argparse
import subprocess

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
    parser = argparse.ArgumentParser()
    parser.add_argument ('--debug', action="store_true", help="Enable debugging")
    ns = parser.parse_args()

    if ns.debug:
        logging.basicConfig (level = logging.DEBUG)

    # Execute tests
    for f in get_tests():
        print (util.green(f))
        fp = os.path.join (qa_dir, f)
        logging.info ('Executing: %s %s'%(sys.executable, fp))
        subprocess.check_call([sys.executable, fp])


if __name__ == '__main__':
    main()
