#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Usage： python update_assetsip.py 1.1.1.1 2.2.2.2
# 1.1.1.1 为原ip, 2.2.2.2 为新ip

import sys, requests, json

jms_url = 'http://192.168.100.104/'
jms_token = 'ad47cab1e364a96fc40899d282989b147c21dfa7'
# jms_token = get_token()
old_ip = sys.argv[1]
new_ip = sys.argv[2]

# def get_token():
#     url = jms_url + 'api/users/v1/auth/'
#     query_args = {
#         "username": "admin",
#         "password": "admin"
#     }
#     response = requests.post(url, data=query_args)
#     return json.loads(response.text)['token']

def update_assetsip():
    global jms_url, jms_token, old_ip, new_ip
    url = jms_url + 'api/assets/v1/assets/?ip=%s' %old_ip
    headers = {
        'Authorization': 'Token ' + jms_token,
        'accept'       : 'application/json',
        'Content-Type' : 'application/json',
    }
    response = requests.get(url, headers=headers)
    try:
        id   = json.loads(response.text)[0]['id']
        hostname = json.loads(response.text)[0]['hostname']
    except IndexError:
        print("\033[32m 资产ip输入错误 \033[0m")
        exit()

    data = data = '{ "ip": "%s", "hostname": "%s" }' %(old_ip, hostname)
    try:
        url_1 = jms_url + '%s/' %id
    except UnboundLocalError:
        print("\033[32m 资产ip输入错误 \033[0m")
        exit()

    r = requests.put(url_1, headers=headers, data=json.dumps(data))
    print ("\033[31m ip已经修改成{} \033[0m".format(json.loads(r.text)['ip']))
    return

try:
    update_assetsip()
except UnboundLocalError:
    print("\033[32m 资产ip输入错误 \033[0m")
    exit()
