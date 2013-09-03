# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import time
import logging
import argparse

import Keys
import utils
import Client
import Config

def main():
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument ('ID',        action="store",      help="ID of the link to ping")
    parser.add_argument ('--confdir', action="store",      help="Customized certificates directory", default=utils.get_basedir_default())
    parser.add_argument ('--debug',   action="store_true", help="Enable debugging")
    ns = parser.parse_args()

    if ns.debug:
        logging.basicConfig (level = logging.DEBUG)

    # Config
    config = Config.Config (ns.confdir)

    # Key manager
    keys = Keys.Manager (ns.confdir)

    # Client
    ping = Client.Ping (config, keys, ns.ID)

    n = 5
    while n > 0:
        ping.execute()
        time.sleep(1)
        n -= 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
