# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import argparse
import logging

import Keys
import utils

def print_keys(keys):
    for k in keys.get_key_list():
        print ("%s id=%s %s" %(k['type'], k['keyid'], ' '.join(k['uids'])))

def main():
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument ('--confdir', action="store",      help="Customized certificates directory", default=utils.get_basedir_default())
    parser.add_argument ('--debug',   action="store_true", help="Enable debugging")
    parser.add_argument ('--list' ,   action="store_true", help="List keys")
    parser.add_argument ('--id',      action="store_true", help="Get the key ID instead of the armored key")
    ns = parser.parse_args()

    if ns.debug:
        logging.basicConfig (level = logging.DEBUG)

    # Key manager
    keys = Keys.Manager (ns.confdir)

    # Print list
    if ns.list:
        print_keys(keys)
        raise SystemExit

    if ns.id:
        print keys.get_gpg_public_keyid()
        raise SystemExit

    # Get key
    print keys.get_gpg_public_key()

if __name__ == '__main__':
    main()
