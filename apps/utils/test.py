#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold
import base64
import hashlib


def gene_pwd(pwd='admin', salt='Fpx2ufNO0'):
    m = hashlib.md5()
    _str = "%s--%s" % (base64.encodebytes(pwd.encode('utf-8')), salt)
    m.update(_str.encode('utf-8'))
    print(m.hexdigest())


if __name__ == '__main__':
    gene_pwd()
