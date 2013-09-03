# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import logging
import argparse
import utils

import Config

def main():
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument ('op', action="store", choices=['add', 'del', 'subscribe', 'unsubscribe'], help="Operation")

    group = parser.add_argument_group('Common parameters')
    group.add_argument ('--confdir', action="store",      help="Customized certificates directory", default=utils.get_basedir_default())
    group.add_argument ('--debug',   action="store_true", help="Enable debugging")

    group = parser.add_argument_group('Operations: add, del')
    group.add_argument ('--cert',    action="store",      help="Certificate file", default="")
    group.add_argument ('--name',    action="store",      help="Name of the link")
    group.add_argument ('--url',     action="store",      help="URL to the uplink host")

    group = parser.add_argument_group('Operations: subscribe, unsubscribe')
    group.add_argument ('--channel', action="store",      help="Subscribe to a channel", metavar="NAME")
    ns = parser.parse_args()

    if ns.debug:
        logging.basicConfig (level = logging.DEBUG)

    #
    # Links
    #

    if ns.op == 'add':
        utils.assert_cli_args (['name', 'cert'], ns)

        config = Config.Config (ns.confdir)
        config.link_add (ns.cert, ns.name, ns.url)
        config.save()

    elif ns.op == 'del':
        utils.assert_cli_args (['name'], ns)

        config = Config.Config (ns.confdir)
        config.link_del (ns.name)
        config.save()


    #
    # Subscriptions
    #

    elif ns.op == 'subscribe':
        utils.assert_cli_args (['name', 'channel'], ns)

        config = Config.Config (ns.confdir)
        config.link_add_subscription (ns.name, ns.channel)
        config.save()

    elif ns.op == 'unsubscribe':
        utils.assert_cli_args (['name', 'channel'], ns)

        config = Config.Config (ns.confdir)
        config.link_del_subscription (ns.name, ns.channel)
        config.save()


if __name__ == '__main__':
    main()
