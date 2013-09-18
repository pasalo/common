# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

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
