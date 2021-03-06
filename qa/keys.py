# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

CACHE_KEYS_DIR = '/var/tmp/pasalo_QA-keys-reuse'

import os
import shutil

import init
init.init()

import colors
import util


def init (force):
    # Cache removal
    if force:
        print (colors.yellow(" * Removing QA key cache %s"%(CACHE_KEYS_DIR)))
        shutil.rmtree (CACHE_KEYS_DIR, ignore_errors=True)
        os.makedirs (CACHE_KEYS_DIR, 0700)

def create (key_id, key_dir, download_dir, public_url=None):
    re_fp = os.path.join(CACHE_KEYS_DIR, key_id)

    # Reuse
    if os.path.exists(re_fp):
        print (colors.yellow(" * Reusing keys from %s" %(re_fp)))
        shutil.copytree (re_fp, key_dir)
        return

    # Create
    print (colors.yellow(" * Creating key %s"%(key_id)))
    util.pasalo_init_path (key_dir, downloads=download_dir, public_url=public_url)

    # Populate cache
    print (colors.yellow(" * Copying key %s to QA cache: %s -> %s"%(key_id, key_dir, re_fp)))
    if not os.path.exists (CACHE_KEYS_DIR):
        os.makedirs (CACHE_KEYS_DIR, 0700)
    shutil.copytree (key_dir, re_fp)
