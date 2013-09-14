# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import sys
import time
import json
import types
import thread
import random
import logging
import StringIO
import subprocess
import multiprocessing

import pycurl
import xattr_wrap as xattr

import HTTPS
import utils


class Base:
    def __init__ (self, config, keys, id_name):
        self.config = config
        self.keys   = keys
        self.id     = id_name

    def _get_url_handler (self, content):
        link  = self.config.get_link_from_id (self.id)
        keyid = link['keyid']

        # Build PING message
        p = self.keys.crypt (content, keyid)
        post = bytearray (p)

        # URL
        url = str(link['url'])
        if not url.startswith('https://'):
            url = 'https://' + url

        # HTTP Request
        out = StringIO.StringIO()
        in_ = StringIO.StringIO(post)

        conn = pycurl.Curl()
        conn.setopt(pycurl.URL, url)
        conn.setopt(pycurl.READFUNCTION, in_.read)
        conn.setopt(pycurl.WRITEFUNCTION, out.write)
        conn.setopt(pycurl.POST, 1)
        conn.setopt(pycurl.POSTFIELDSIZE, len(post))
        conn.setopt(pycurl.SSL_VERIFYPEER, 0)
        conn.setopt(pycurl.SSL_VERIFYHOST, 0)

        conn.out = out
        return conn

    def _build_operation (self, op, parameters={}):
        op = {'op': op}
        op.update (parameters)
        return json.dumps(op)

    def execute (self, content):
        conn = self._get_url_handler (content)
        conn.perform()
        conn.close()

        response = conn.out.getvalue()

        # Process response
        received = self.keys.decrypt(response)
        return received


class Ping (Base):
    def __init__ (self, config, keys, id):
        Base.__init__ (self, config, keys, id)

    def execute (self):
        time1 = time.time()

        op = self._build_operation ('ping')
        received = Base.execute (self, op)

        if received.data != 'PONG':
            logging.error ("Wrong PING response: " + str(received.data))
            return

        time2 = time.time()
        print "Response from %s: time=%01.02fs" %(received.key_id, time2-time1)


class ChannelList (Base):
    def __init__ (self, config, keys, name_id):
        Base.__init__ (self, config, keys, name_id)

    def execute (self):
        op = self._build_operation ('get channel list')
        received = Base.execute (self, op)
        return json.loads(received.data)


class FileList (Base):
    def __init__ (self, config, keys, name_id, channels):
        Base.__init__ (self, config, keys, name_id)
        if type(channels) != list:
            self.channels = [c.strip() for c in channels.split(',')]
        else:
            self.channels = channels

    def execute (self):
        op = self._build_operation ('get file list', {'channels': self.channels})
        received = Base.execute (self, op)
        return json.loads(received.data)



class Download (Base):
    def __init__ (self, config, download_dir, keys, name_id, channel, filename, callback_step=None):
        Base.__init__ (self, config, keys, name_id)
        self.download_dir  = download_dir
        self.channel       = channel
        self.filename      = filename
        self.callback_step = callback_step

    def execute (self):
        op = self._build_operation ('download file', {'channel': self.channel, 'file': self.filename})

        def progress(download_t, download_d, upload_t, upload_d):
            self.download_t = download_t
            self.download_d = download_d
            self.upload_t   = upload_t
            self.upload_d   = upload_d

            if self.callback_step:
                self.callback_step (download_t, download_d)

            if download_t:
                percent = '%.02f' %((download_d * 100.0) / (download_t))
                print "Received %s (%s%%)" %(utils.format_size(download_d), percent)
            else:
                print "Received %s" %(utils.format_size(download_d))


        # Prepare final file
        #
        out_dir = os.path.join (self.download_dir, self.channel)
        if not os.path.exists (out_dir):
            os.makedirs (out_dir, 0700)

        out_fullpath = os.path.join (out_dir, self.filename)
        out_f = open (out_fullpath, 'w+')

        # Decrypt
        #
        p = self.keys.decrypt_popen (stdin  = subprocess.PIPE,
                                     stdout = out_f,
                                     stderr = sys.stderr)

        # Handle download
        conn = self._get_url_handler (op)
        conn.setopt (pycurl.NOPROGRESS, 0)
        conn.setopt (pycurl.PROGRESSFUNCTION, progress)
        conn.setopt (pycurl.WRITEFUNCTION, p.stdin.write)
        conn.perform()

        # Set file attributes
        xattr.setxattr (out_fullpath, 'md5_time', str(time.time()))
        xattr.setxattr (out_fullpath, 'md5', utils.md5_file(out_fullpath))

        # Clean up
        conn.close()
        p.kill()



class Sync (Base):
    def __init__ (self, config, download_dir, keys, name_id):
        Base.__init__ (self, config, keys, name_id)
        self.download_dir = download_dir

    def execute (self):
        # Channels
        lst = ChannelList (self.config, self.keys, self.id)
        channels = lst.execute()
        print "channels", channels

        # Files
        lst = FileList (self.config, self.keys, self.id, ','.join(channels))
        remote_files = lst.execute()
        print "remote_files", remote_files

        # Check local files
        new_files = []

        for remote_file in remote_files:
            fp = os.path.join (self.download_dir, remote_file['path'])

            # No local version
            if not os.path.exists (fp):
                new_files.append (remote_file)
                continue

            # Outdated local version
            size      = os.path.getsize(fp)
            attr_md5  = xattr.getxattr (fp, 'md5')
            attr_time = utils.getxattr (fp, 'md5_time', 0)

            if remote_file['size'] != size or \
               remote_file['md5']  != attr_md5:
                new_files.append (remote_file)
                continue

            logging.info ("%s is up to date" %(remote_file['path']))

        # New files to fetch
        for f in new_files:
            channel, filename = f['path'].split('/', 1)

            download = Download (self.config, self.download_dir, self.keys, self.id, channel, filename)
            download.execute()


class Client (Base):
    def __init__ (self, config, download_dir, keys, name_id):
        Base.__init__ (self, config, keys, name_id)
        self.download_dir = download_dir

    def execute (self, max_times=None):
        n = 0
        while True:
            sync = Sync (self.config, self.download_dir, self.keys, self.id)
            sync.execute()

            # Check limit
            n += 1
            if max_times and max_times >= n:
                break

            # Wait until next iteration
            lapse = random.randint(10*60, 60*60)
            logging.info ("Sleeping for %d secs" %(lapse))
            time.sleep(lapse)


class Client_Server:
    def __init__ (self, config, download_dir, keys, channels, port, interface):
        self.keys         = keys
        self.config       = config
        self.download_dir = download_dir
        self.channels     = channels
        self.port         = port
        self.interface    = interface

    def _launch_server (self):
        def thread_logic():
            srv = HTTPS.Server (self.keys, self.channels, self.config, self.port, self.interface)
            srv.run()

        p = multiprocessing.Process (target=thread_logic, args=())
        p.start()
        p.join()

    def execute (self, max_times=None):
        # Server
        self._launch_server()

        # Client
        clients = []
        for link_name in self.config.get_link_names():
            l = self.config.get_link_from_id (link_name)
            if l.get('url'):
                clients.append (link_name)

        while True:
            for link_name in clients:
                client = Client.Client (self.config, self.download_dir, self.keys, link_name)
                client.execute (max_times=1)

            # Wait until next iteration
            lapse = random.randint(10*60, 60*60)
            logging.info ("Sleeping for %d secs" %(lapse))
            time.sleep(lapse)
