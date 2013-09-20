# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import sys
import json
import fnmatch
import StringIO

import pycurl

import Keys
import utils


class Config:
    def __init__ (self, conf_basedir):
        self.conf_basedir = conf_basedir
        self.config_fp    = utils.get_config_fp(conf_basedir)
        self.config       = {}

        self.__read()

    def __read (self):
        with open(self.config_fp, 'r') as f:
            self.config = json.load(f)

    def save (self):
        with open(self.config_fp, 'w+') as f:
            json.dump (self.config, f)

    #
    # Link
    #
    def get_link_from_url (self, url):
        for link in self.config.get('links',[]):
            if url in link.get('url', ''):
                return link

    def get_link_from_id (self, id_name):
        for link in self.config.get('links',[]):
            if id_name == link.get('id', ''):
                return link

    def get_link_names (self):
        return [l['id'] for l in self.config.get('links',[])]


    def __read_cert (self, cert):
        if not cert or cert == '-':
            return sys.stdin.read()

        elif cert.startswith('http'):
            out = StringIO.StringIO()

            conn = pycurl.Curl()
            conn.setopt(pycurl.URL, cert)
            conn.setopt(pycurl.WRITEFUNCTION, out.write)
            conn.setopt(pycurl.SSL_VERIFYPEER, 0)
            conn.setopt(pycurl.SSL_VERIFYHOST, 0)
            conn.perform()
            conn.close()

            print out.getvalue()
            return out.getvalue()

        else:
            with open (cert, 'r') as f:
                return f.read()

    def link_add (self, cert_filename, id_name, url=None):
        # Read key
        cont = self.__read_cert (cert_filename)

        # Add key to keyring
        keys = Keys.Manager (self.conf_basedir)
        import_result = keys.add_gpg_key (cont)

        fingerprint = import_result.fingerprints[0]
        key = keys.get_gpg_key_by_fingerprint (fingerprint)

        # Add the entry
        dup = False
        for l in self.config.get('links',[]):
            if l['id'] == id_name or \
               l['keyid'] == key['keyid']:
                dup = True
                break

        if not dup:
            entry = {
                'keyid': key['keyid'],
                'id':    id_name,
            }

            if url:
                entry['url'] = url

            links = self.config.get('links',[])
            links.append (entry)
            self.config['links'] = links

    def link_del (self, id_name):
        for l in self.config.get('links',[]):
            if l['id'] == id_name:
                del (self.config[l])
                break

    #
    # Subscriptions
    #

    def link_add_subscription (self, link_name, channel):
        for l in self.config.get('links',[]):
            if l['id'] != link_name:
                continue

            subscription = l.get('subscriptions', [])
            if not channel in subscription:
                subscription.append (channel)
                l['subscriptions'] = subscription

    def link_del_subscription (self, link_name, channel):
        for l in self.config.get('links',[]):
            if l['id'] != link_name:
                continue

            new_subscriptions = []
            for e in l.get('subscriptions', []):
                if not fnmatch.fnmatch (e, channel):
                    new_subscriptions.append (e)

            l['subscriptions'] = new_subscriptions
