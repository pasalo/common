# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os

def init():
    # Import from QA/../
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if not parentdir in os.sys.path:
        os.sys.path.insert(0,parentdir)
