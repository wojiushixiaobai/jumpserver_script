#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Usage： python update_assetsip.py 1.1.1.1
# 1.1.1.1 为要添加的新资产 ip

import sys, requests, json

jms_url = 'http://192.168.100.104/'
jms_token = 'ad47cab1e364a96fc40899d282989b147c21dfa7'
admin_user = '2efab732-e267-46bc-a8ba-d5c5cb0c5195'
# jms_token = get_token()
ip = sys.argv[1]

# def get_token():
#     url = 'https://demo.jumpserver.org/api/users/v1/auth/'
#     query_args = {
#         "username": "admin",
#         "password": "admin"
#     }
#     response = requests.post(url, data=query_args)
#     return json.loads(response.text)['token']

def create_assets():
    global jms_url, jms_token,ip

    headers = {
        'Authorization': 'Token ' + jms_token,
        'accept'       : 'application/json',
        'Content-Type' : 'application/json',
    }

    url = jms_url + 'api/assets/v1/assets/'

    data = { 'ip': '%s' % ip, 'hostname': '%s' % ip, 'protocols': [ 'ssh/22' ], 'platform': 'Linux', 'is_active': 'true', 'admin_user': '%s' % admin_user }
    r = requests.post(url, headers=headers, data=json.dumps(data))

    try:
        print ("\033[31m 资产{}已经添加完成 \033[0m".format(json.loads(r.text)['ip']))
    except KeyError:
        print("\033[32m 请确认ip、token、admin_user设置正确 \033[0m")
    except ValueError:
       print("\033[32m Url地址有误 \033[0m")

create_assets()
