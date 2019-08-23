#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Usage:
# pip install python-socketio==1.8.3 -i https://mirrors.aliyun.com/pypi/simple/
# pip install paramiko -i https://mirrors.aliyun.com/pypi/simple/
# python ssh_check.py

import paramiko, socket, sys, re

file = '11.csv'

def get_Assets():
    assets       = {}
    f            = open(file,'r')
    lines        = f.readlines()
    f.close()
    for line in lines:
        hostname = line.split(',')[0]
        assets.setdefault('hostname', []).append(hostname)
        port     = line.split(',')[1]
        assets.setdefault('port', []).append(port)
        username = line.split(',')[2]
        assets.setdefault('username', []).append(username)
        password = line.split(',')[3]
        assets.setdefault('password', []).append(password)

    return assets

def manual_auth():
    assets   = get_Assets()
    hostname = assets['hostname']
    port     = assets['port']
    username = assets['username']
    password = assets['password']
    x        = len(hostname)
    i        = 0
    while i < x:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((hostname[i],int(port[i])))
        except Exception, e:
            # print '*** Connect failed: ' + str(e)
            print u'%s\t%s\t\033[33m Unknown \033[0m' % (hostname[i],port[i])
            i += 1
            continue
        t = paramiko.Transport(sock)
        try:
            t.start_client()
        except paramiko.SSHException:
            # print '*** SSH negotiation failed.'
            print u'%s\t%s\t\033[34m Failed \033[0m' % (hostname[i],port[i])
        try:
            t.auth_password(username[i], password[i])
            if t.is_authenticated():
                print u'%s\t%s\t%s\t%s\t\033[32m Success \033[0m' % (hostname[i],port[i],username[i],password[i])
            # else:
                # print u'%s\t%s\t%s\t%s\t\033[33m Unknown \033[0m' % (hostname[i],port[i],username[i],password[i])
        except:
            print u'%s\t%s\t%s\t%s\t\033[31m Error \033[0m' % (hostname[i],port[i],username[i],password[i])
        t.close()
        i += 1

manual_auth()
