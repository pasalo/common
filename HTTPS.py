# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

## http://twistedmatrix.com/documents/current/web/examples/index.html

import os
import sys
import json
import logging
import tempfile

import Keys
import LinkInfo
import Exceptions

from twisted.web import server, resource
from twisted.internet import reactor, ssl
from twisted.python.log import err
from twisted.protocols.basic import FileSender
from twisted.python import log


class Server_Resources (resource.Resource):
    isLeaf = False

    def __init__ (self, server):
        resource.Resource.__init__ (self)
        self.server = server

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_POST (self, request):
        # Read POST into a temporary file
        tmpfile = tempfile.TemporaryFile()
        while True:
            data = request.content.read(512 * 1024)
            if not data:
                break
            tmpfile.write (data)

        tmpfile.seek(0)

        # Decrypt it
        decrypted = self.server.key_manager.decrypt_file (tmpfile)

        request.setHeader("content-type", "text/plain")

        # Make sure we know the client
        if not self.server.key_manager.is_gpg_key_in_ring (decrypted.key_id):
            print ("WARNING: Unknown client (Key ID: %s)" %(decrypted.key_id))
            request.setResponseCode(511)
            return "ERROR: I'm sorry sir, I don't know any Mr. %s"%(str(decrypted.key_id))

        tmpfile.close()

        # JSON parse
        op = json.loads (decrypted.data)

        # Operations
        if op['op'] == 'ping':
            return self.server.key_manager.crypt ("PONG", decrypted.key_id)

        elif op['op'] == 'get channel list':
            channels = self.server.channel_manager.get_local_channels()
            channels_json = json.dumps(channels)
            channels_crypted = self.server.key_manager.crypt (channels_json, decrypted.key_id)
            return channels_crypted

        elif op['op'] == 'get file list':
            files = self.server.channel_manager.get_local_files(op['channels'])
            files_json = json.dumps(files)
            return self.server.key_manager.crypt (files_json, decrypted.key_id)

        elif op['op'] == 'download file':
            f = self.server.channel_manager.get_filestream (op['channel'], op['file'])
            p = self.server.key_manager.crypt_file_popen (f, decrypted.key_id)
            d = FileSender().beginFileTransfer(p.stdout, request)

            def cbFinished(ignored):
                p.kill()
                p.wait()
                request.finish()

            d.addErrback(err).addCallback(cbFinished)
            return server.NOT_DONE_YET



class Server_Resources_Key (resource.Resource):
    isLeaf = True

    def __init__ (self, server):
        resource.Resource.__init__ (self)
        self.server = server

    def render_GET (self, request):
        li = LinkInfo.LinkInfo()
        return li.get_uplink_info (self.server.config.conf_basedir)




class Server:
    DEFAULT_TCP_PORT = 443

    def __init__ (self, key_manager, channels, config, port=None, interface='', serve_key=None):
        self.key_manager     = key_manager
        self.channel_manager = channels
        self.config          = config
        self.tcp_port        = port or self.DEFAULT_TCP_PORT
        self.interface       = interface
        self.serve_key       = serve_key

        # Activate Twister logging
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            log.startLogging(sys.stdout)


    def __do_serve_key_checks (self):
        uplink_info = self.config.get_uplink_info()
        if not uplink_info.get('public_url'):
            raise Exceptions.Fatal ("Missing 'public_url' property. Cannot serve the public key without it.")

    def run(self):
        tlsctxFactory = ssl.DefaultOpenSSLContextFactory (self.key_manager.https_key,
                                                          self.key_manager.https_crt,
                                                          ssl.SSL.TLSv1_METHOD)

        root = Server_Resources(self)
        if self.serve_key:
            self.__do_serve_key_checks()
            root.putChild ('key', Server_Resources_Key(self))

        logging.info ("Listerning new connection on port %s" %(self.tcp_port))
        reactor.listenSSL (self.tcp_port, server.Site(root), tlsctxFactory, interface=self.interface)

        print ("Pasalo server running port %s"%(self.tcp_port))
        reactor.run()
