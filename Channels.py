# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import sys
import json
import time
import utils
import xattr_wrap as xattr

class Channel:
    def __init__ (self, name):
        self.name = name


class Manager:
    def __init__ (self, config):
        self.config = config

    def get_local_channels (self):
        downloads_dir = self.config.config['downloads']

        channels = []
        for f in os.listdir(downloads_dir):
            fp = os.path.join (downloads_dir, f)
            if not os.path.isdir (fp):
                continue
            channels.append (f)

        return channels

    def get_local_files (self, channels):
        downloads_dir = self.config.config['downloads']

        files = []
        for channel in channels:
            if '..' in channel:
                continue

            dir_fp = os.path.join (downloads_dir, channel)

            if not os.path.exists (dir_fp):
                continue
            if not os.path.isdir (dir_fp):
                continue

            for f in os.listdir (dir_fp):
                if f[0] in '.#~':
                    continue

                fname      = os.path.join (channel, f)
                fname_fp   = os.path.join (dir_fp, f)
                fname_size = os.path.getsize(fname_fp)

                # No dirs within channels
                if not os.path.isfile (fname_fp):
                    continue

                utils.set_md5_attr (fname_fp, force=False)
                fname_md5 = xattr.getxattr (fname_fp, 'md5')

                files.append ({'path': fname, 'size': fname_size, 'md5': fname_md5})

        return files


    def get_filestream (self, channel, filename):
        if '..' in channel or '..' in filename:
            return

        downloads_dir = self.config.config['downloads']
        fp = os.path.join (downloads_dir, channel, filename)
        if os.path.exists (fp):
            return open (fp, 'r')


    def get_all (self):
        links = self.config.get('links',[])

        # Links's channels aggregation
        channels = []
        for link_channels in [l['downstream_channels'] for l in links]:
            channels += link_channels

        # Remove duplicates
        channels = list(set(channels))

        return channels
