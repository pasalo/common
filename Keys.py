# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import sys
import gnupg
import logging
from subprocess import Popen, PIPE

import utils


def get_gpg_binary():
    for binary in ('gpg2', 'gpg'):
        tmp = utils.which (binary)
        if tmp:
            return tmp

class Manager:
    KEY_TYPE     = 'RSA'
    KEY_LENGTH   = 4096
    NAME_COMMENT = "Downstream Flow"

    def __init__ (self, basedir):
        # GPG
        self.gpg_basedir = os.path.join (basedir, 'gpg')

        self.gpg = gnupg.GPG (gnupghome = self.gpg_basedir,
                              gpgbinary = get_gpg_binary(),
                              verbose   = False)
        self.gpg.encoding = 'utf-8'

        # HTTPS
        self.https_basedir = os.path.join (basedir, 'https')
        self.https_key     = os.path.join (self.https_basedir, 'server.key')
        self.https_crt     = os.path.join (self.https_basedir, 'server.crt')
        self.https_req     = os.path.join (self.https_basedir, 'server.req')
        self.https_ca_key  = os.path.join (self.https_basedir, 'ca.key')
        self.https_ca_crt  = os.path.join (self.https_basedir, 'ca.crt')


    #
    # GPG
    #
    def __check_gpg_keys_dir (self):
        fp_pub = os.path.join (self.gpg_basedir, 'pubring.gpg')
        fp_sec = os.path.join (self.gpg_basedir, 'secring.gpg')

        if not os.path.isfile (fp_pub) or \
           not os.path.isfile (fp_sec):
            return False

        return True

    def keys_gpg_create (self, email, name):
        if self.__check_gpg_keys_dir():
            logging.debug ("Using GPG keys at %s" %(self.gpg_basedir))
            return

        if not os.path.isdir (self.gpg_basedir):
            os.makedirs (self.gpg_basedir, 0700)

        key_input = self.gpg.gen_key_input (key_type     = self.KEY_TYPE,
                                            key_length   = self.KEY_LENGTH,
                                            name_comment = self.NAME_COMMENT,
                                            name_real    = name,
                                            name_email   = email)

        logging.info ("Please, wait. Generating key...")
        key = self.gpg.gen_key (key_input)
        logging.info ("Generated key %s" %(key.fingerprint))


    def is_gpg_key_in_ring (self, keyid):
        return keyid in [e['keyid'] for e in self.gpg.list_keys()]

    def get_gpg_key_by_fingerprint (self, fingerprint):
        for k in self.gpg.list_keys():
            if k['fingerprint'] == fingerprint:
                return k

    def get_gpg_public_key (self):
        keys = self.gpg.list_keys()
        assert (len(keys))

        keyid = keys[0]['keyid']
        return self.gpg.export_keys(keyid)

    def get_gpg_public_keyid (self):
        keys = self.gpg.list_keys()
        assert (len(keys))
        return keys[0]['fingerprint']

    def get_gpg_public_fingerprint (self):
        keys = self.gpg.list_keys()
        assert (len(keys))
        return keys[0]['fingerprint']

    def get_gpg_public_keyid (self):
        keys = self.gpg.list_keys()
        assert (len(keys))
        return keys[0]['keyid']

    def get_key_list (self):
        return self.gpg.list_keys()

    def add_gpg_key (self, key_armored):
        return self.gpg.import_keys (key_armored)

    def crypt (self, data, keyid_to, fingerprint_from=None):
        finger = fingerprint_from or self.get_gpg_public_fingerprint()
        return self.gpg.encrypt (data, keyid_to, armor=False, sign=finger, always_trust=True).data


    def crypt_file_popen (self, stream, keyid_to, fingerprint_from=None):
        finger = fingerprint_from or self.get_gpg_public_fingerprint()

        args = ['--encrypt', '--recipient "%s"'%(keyid_to), '--sign --default-key "%s"'%(finger),  "--always-trust"]
        cmd  = ' '.join(self.gpg.make_args(args, False))
        p = utils.PopenAsync (cmd, stdin=stream)
        os.dup2 (sys.stderr.fileno(), p.stderr.fileno())
        return p

    def decrypt (self, data):
        return self.gpg.decrypt (data, always_trust=True)

    def decrypt_file (self, fstream):
        return self.gpg.decrypt_file (fstream, always_trust=True)

    def decrypt_file_to_path (self, fstream, out_fullpath):
        return self.gpg.decrypt_file (fstream, output=out_fullpath, always_trust=True)

    def decrypt_file_callback (self, stream, callback):
        args = ['--decrypt', "--always-trust"]
        cmd  = ' '.join(self.gpg.make_args(args, False))
        p = utils.PopenAsync (cmd, stdin=stream)

        os.dup2 (sys.stderr.fileno(), p.stderr.fileno())

        while True:
            decrypted_block = p.stdout.read (1024*1024)
            if not decrypted_block:
                logging.info ("Read EOF from gpg")
                break
            logging.info ("Read %d from gpg" %(len(crypted_block)))
            callback (decrypted_block)

    def decrypt_popen (self, **vargs):
        args = ['--decrypt', "--always-trust"]
        cmd  = ' '.join(self.gpg.make_args(args, False))

        return utils.PopenAsync (cmd, **vargs)



    #
    # HTTPS
    #
    def __check_https_keys_dir (self):
        if not os.path.isfile (self.https_key) or \
           not os.path.isfile (self.https_crt):
            return False

        return True

    def keys_https_create (self):
        if self.__check_https_keys_dir():
            logging.info ("Using TLS key+cert at %s" %(self.https_basedir))
            return

        if not os.path.isdir (self.https_basedir):
            os.makedirs (self.https_basedir, 0700)

        def run (cmd):
            logging.debug ('--->' + cmd)
            os.system (cmd)

        run ("openssl genrsa 4096 > %s" %(self.https_ca_key))
        run ("openssl req -new -x509 -nodes -days 3600 -batch -key %s > %s" %(self.https_ca_key, self.https_ca_crt))
        run ("openssl req -newkey rsa:2048 -days 3600 -batch -nodes -keyout %s > %s" %(self.https_key, self.https_req))
        run ("openssl x509 -req -in %s -days 3600 -CA %s -CAkey %s -set_serial 01 > %s" %(self.https_req, self.https_ca_crt, self.https_ca_key, self.https_crt))

    def keys_create (self):
        self.keys_gpg_create()
        self.keys_https_create()
