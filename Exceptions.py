# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

class Fatal (Exception):
    def __init__(self, msg):
        Exception.__init__ (self)
        self.msg = msg
