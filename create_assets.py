#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Usage： python update_assetsip.py 1.1.1.1
# 1.1.1.1 为要添加的新资产 ip

import sys, requests, json

jms_url        = 'http://192.168.1.118/'
admin_name     = 'Linux_root'
admin_username = 'root'
admin_password = 'root'
ip = sys.argv[1]

def get_token():
    url = jms_url + 'api/users/v1/auth/'
    query_args = {
        "username": "admin",
        "password": "admin"
    }
    response = requests.post(url, data=query_args)
    try:
        return json.loads(response.text)['token']
    except KeyError:
        print("\033[32m 获取token错误, 请检查账户密码 \033[0m")
        exit()

def create_adminuser():

    jms_token = get_token()

    url = jms_url + 'api/assets/v1/admin-user/'
    headers = {
        'Authorization': 'Bearer ' + jms_token,
        'accept'       : 'application/json',
        'Content-Type' : 'application/json'
    }

    data = '{ "name": "%s", "username": "%s", "password": "%s" }' %(admin_name, admin_username, admin_password)
    response = requests.post(url, headers=headers, data=data)
    try:
        return json.loads(response.text)['id']
    except KeyError:
        url_1 = url + '?name=%s' %admin_name
        response = requests.get(url_1, headers=headers)
        return json.loads(response.text)[0]['id']

def create_assets():

    jms_token = get_token()
    admin_id  = create_adminuser()

    headers = {
        'Authorization': 'Bearer ' + jms_token,
        'accept'       : 'application/json',
        'Content-Type' : 'application/json'
    }

    url = jms_url + 'api/assets/v1/assets/'
    data = '{ "ip": "%s", "hostname": "%s", "protocols": [ "ssh/22" ], "platform": "Linux", "is_active": "true", "admin_user": "%s" }' %(ip, ip, admin_id)
    response = requests.post(url, headers=headers, data=data)

    try:
        print ("\033[31m 资产{}已经添加完成 \033[0m".format(json.loads(response.text)['ip']))
    except KeyError:
        print("\033[32m 请确认ip、token、admin_user设置正确 \033[0m")
    except ValueError:
        print("\033[32m Url地址有误 \033[0m")

create_assets()
