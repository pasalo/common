# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import time

def init_coverage_file (extension):
    name = '.coverage'
    if extension:
        name += '.%s-%s'%(os.path.basename(extension), str(time.time()))
    os.environ['COVERAGE_FILE'] = name

def init_coverage (extension=None):
    # Child-process coverage support
    if os.environ.has_key("COVERAGE_PROCESS_START"):
        # Set destination file
        init_coverage_file (extension)

        # Import module
        try:
            import coverage
            coverage.process_startup()
        except ImportError:
            pass
