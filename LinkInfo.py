# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import sys
import json
import logging

import Keys
import Config


class LinkInfo:
    def __init__ (self):
        None

    def get_uplink_info (self, confdir):
        # Get certificate
        keys = Keys.Manager (confdir)
        cert = str(keys.get_gpg_public_key())

        # Get the rest of the relevant information
        config = Config.Config (confdir)
        info = config.get_uplink_info()
        info['key'] = cert

        # JSON'ify
        return json.dumps(info)

    def read_uplink_info (self, cont):
        self.info = json.loads(cont)

    def get (self, *args):
        return self.info.get(*args)
    def __getitem__ (self, key):
        return self.info.get(key)
