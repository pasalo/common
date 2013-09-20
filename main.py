# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import sys
import time
import colors
import random
import logging
import argparse

import Keys
import utils
import HTTPS
import Config
import Client
import Channels
import Exceptions


def _main():
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument ('op', action="store", choices=['server', 'channels', 'ls', 'download', 'sync', 'client', 'run'], help="Operation")

    group = parser.add_argument_group('Common parameters')
    group.add_argument ('--confdir',   action="store",      help="Customized configuration directory", default=utils.get_basedir_default())
    group.add_argument ('--debug',     action="store_true", help="Enable debugging")

    group = parser.add_argument_group('Server')
    group.add_argument ('--port',      action="store",      help="Customized HTTPS port (Default: 443)", type=int)
    group.add_argument ('--bind',      action="store",      help="The hostname to bind (Default: all)", default='')
    group.add_argument ('--key',       action="store_true", help="Serve public key from /key")

    group = parser.add_argument_group('Client')
    group.add_argument ('--downloads', action="store",      help="Downloads directory", metavar="PATH", default=utils.get_downloads_default())
    group.add_argument ('--name',      action="store",      help="Name of the host to connect to")
    group.add_argument ('--channels',  action="store",      help="Channels", metavar="NAMES")
    group.add_argument ('--file',      action="store",      help="Filename")
    ns = parser.parse_args()

    if ns.debug:
        logging.basicConfig (level = logging.DEBUG)

    # Key manager
    keys = Keys.Manager (ns.confdir)

    # Config
    config = Config.Config (ns.confdir)

    # Channels
    channels = Channels.Manager (config)

    # Server
    if ns.op == 'server':
        srv = HTTPS.Server (keys, channels, config, ns.port, ns.bind, ns.key)
        srv.run()

    # Client
    elif ns.op == 'channels':
        utils.assert_cli_args (['name'], ns)
        lst = Client.ChannelList (config, keys, ns.name)
        channel_list = lst.execute()
        for channel in channel_list:
            print (channel)

    elif ns.op == 'ls':
        utils.assert_cli_args (['name','channels'], ns)
        lst = Client.FileList (config, keys, ns.name, ns.channels)
        files = lst.execute()
        for f in files:
            print ("%s (%s) size=%s" %(f['path'], f['md5'], f['size']))

    elif ns.op == 'download':
        utils.assert_cli_args (['name','channels', 'file'], ns)
        upd = Download_Reporter()
        dwn = Client.Download (config, ns.downloads, keys, ns.name, ns.channels, ns.file, upd.step_cb, upd.finished_cb)
        dwn.execute()

    elif ns.op == 'sync':
        utils.assert_cli_args (['name'], ns)
        upd = Download_Reporter()
        sync = Client.Sync (config, ns.downloads, keys, ns.name, upd.step_cb, upd.finished_cb)
        sync.execute()

    elif ns.op == 'client':
        utils.assert_cli_args (['name'], ns)
        client = Client.Client (config, ns.downloads, keys, ns.name)
        client.execute()

    # Server + Client
    elif ns.op == 'run':
        upd = Download_Reporter()
        client_server = Client.Client_Server (config, ns.downloads, keys, channels, ns.port, ns.bind, upd.step_cb, upd.finished_cb)
        client_server.execute()


class Download_Reporter:
    def __init__ (self):
        self.time_start = time.time()

    def step_cb (self, filename, download_t, download_d):
        lapse = time.time() - self.time_start
        speed = utils.format_size(download_d/lapse)

        string = "%s - %s (%s/s)" %(filename, utils.format_size(download_d), speed)
        string += ' ' * 8
        string += '\b' * len(string)

        sys.stdout.write (string)
        sys.stdout.flush()

    def finished_cb (self, dwn_obj):
        print


def main():
    try:
        _main()
    except Exceptions.Fatal, e:
        print >> sys.stderr, colors.red('[ERROR]') + ' ' + e.msg


if __name__ == '__main__':
    random.seed()
    main()
