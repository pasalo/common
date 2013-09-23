# -*- mode: python; coding: utf-8 -*-

__author__    = "Alvaro Lopez Ortega"
__email__     = "alvaro@alobbs.com"
__copyright__ = "Copyright (C) 2013 Alvaro Lopez Ortega"

import os
import json
import xattr
import fcntl

xattr_supported = True


def _faked_setxattr (path, key, value):
    path_dir   = os.path.dirname(path)
    path_name  = os.path.basename(path)
    props_file = os.path.join (path_dir, '.pasalo.props')

    # Read properties file
    f = open (props_file, 'rw+')
    fcntl.flock(f, fcntl.LOCK_EX)
    cont = f.read() or '{}'

    # Set property
    props = json.loads(cont)
    if not props.has_key(path_name):
        props[path_name] = {}

    props[path_name][key] = value

    # Write file
    f.seek(0)
    f.write(json.dumps(props))
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()

def _faked_getxattr (path, key):
    path_dir   = os.path.dirname(path)
    path_name  = os.path.basename(path)
    props_file = os.path.join (path_dir, '.pasalo.props')

    if not os.path.exists (props_file):
        return None

    f = open (props_file, 'r')
    fcntl.flock(f, fcntl.LOCK_EX)

    props = json.loads(f.read())

    if not props.has_key(path_name):
        return None

    value = props[path_name].get(key)

    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()

    return value

def _faked_listxattr (path):
    path_dir = os.path.dirname(path)
    path_name  = os.path.basename(path)
    props_file = os.path.join (path_dir, '.pasalo.props')

    if not os.path.exists (props_file):
        return {}

    f = open (props_file, 'r')
    fcntl.flock(f, fcntl.LOCK_EX)

    props = json.loads(f.read())

    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()

    return props.get(path_name)


def setxattr (path, key, value):
    global xattr_supported
    if xattr_supported:
        try:
            return xattr.setxattr (path, key, value)
        except IOError, e:
            if e.errno == 95: # Operation not supported
                xattr_supported = False
            else:
                raise

    return _faked_setxattr (path, key, value)

def getxattr (path, key):
    global xattr_supported
    if xattr_supported:
        try:
            return xattr.getxattr (path, key)
        except IOError, e:
            if e.errno == 95: # Operation not supported
                xattr_supported = False
            else:
                raise

    return _faked_getxattr (path, key)

def listxattr (path):
    global xattr_supported
    if xattr_supported:
        try:
            return xattr.listxattr (path)
        except IOError, e:
            if e.errno == 95: # Operation not supported
                xattr_supported = False
            else:
                raise

    return _faked_listxattr (path)
