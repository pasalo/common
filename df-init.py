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

CFG_EXAMPLE_SERVER = """\
{
    "version": 1
}
"""

CFG_EXAMPLE_CLIENT = """\
{
    "version": 1
}
"""

def main():
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument ('--confdir',   action="store",      help="Customized certificates directory", default=utils.get_basedir_default())
    parser.add_argument ('--downloads', action="store",      help="Downloads directory", default=utils.get_downloads_default())
    parser.add_argument ('--debug',     action="store_true", help="Enable debugging")
    parser.add_argument ('--force',     action="store_true", help="Force operation")
    parser.add_argument ('--name',      action="store",      help="Your name")
    parser.add_argument ('--email',     action="store",      help="Your email")
    parser.add_argument ('--add-cfg',   action="store",      help="Add configuration file: (srv or client)")
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
    keys.keys_gpg_create(name=ns.name, email=ns.email)
    keys.keys_https_create()

    # Download directory
    if not os.path.exists (ns.downloads):
        os.makedirs (ns.downloads, 0700)

    # Configuration file
    config_fp = utils.get_config_fp (ns.confdir)
    if ns.add_cfg == 'srv':
        with open(config_fp, 'w+') as f:
            f.write (CFG_EXAMPLE_SERVER)
    elif ns.add_cfg == 'client':
        with open(config_fp, 'w+') as f:
            f.write (CFG_EXAMPLE_CLIENT)

    # Add configuration paramaters
    config = Config.Config (ns.confdir)
    config.config['downloads'] = ns.downloads
    config.save()


if __name__ == '__main__':
    main()
