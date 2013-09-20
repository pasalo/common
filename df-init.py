# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import sys
import logging
import argparse

import Keys
import Config
import utils

CFG_EXAMPLE = """\
{
    "version": 1
}
"""

def main():
    default_name  = utils.get_default_name()
    default_email = utils.get_default_email()

    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument ('--confdir',    action="store",      help="Customized certificates directory", default=utils.get_basedir_default())
    parser.add_argument ('--downloads',  action="store",      help="Downloads directory", default=utils.get_downloads_default())
    parser.add_argument ('--debug',      action="store_true", help="Enable debugging")
    parser.add_argument ('--force',      action="store_true", help="Force operation")
    parser.add_argument ('--name',       action="store",      help="Your name (Default: %s)"%(default_name), default=default_name)
    parser.add_argument ('--email',      action="store",      help="Your email (Default: %s)"%(default_email), default=default_email)
    parser.add_argument ('--public_url', action="store",      help="Address clients connect to")
    ns = parser.parse_args()

    if ns.debug:
        logging.basicConfig (level = logging.DEBUG)

    # Already inited?
    gpg_dir = os.path.join (ns.confdir, 'gpg')
    if os.path.exists (gpg_dir) and not ns.force:
        print >> sys.stderr, "ERROR: Directory exists %s"%(ns.confdir)
        raise SystemExit

    # Create GPG keys
    keys = Keys.Manager (ns.confdir)
    keys.keys_gpg_create(ns.email, name=ns.name)
    keys.keys_https_create()

    # Download directory
    if not os.path.exists (ns.downloads):
        os.makedirs (ns.downloads, 0700)

    # Configuration file
    config_fp = utils.get_config_fp (ns.confdir)
    with open(config_fp, 'w+') as f:
        f.write (CFG_EXAMPLE)

    # Add configuration paramaters
    config = Config.Config (ns.confdir)
    config.config['downloads'] = ns.downloads

    if ns.public_url:
        config.config['public_url'] = ns.public_url

    config.save()


if __name__ == '__main__':
    main()
