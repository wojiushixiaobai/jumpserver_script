#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Usage： python update_assetsip.py 1.1.1.1 2.2.2.2
# 1.1.1.1 为原ip, 2.2.2.2 为新ip

import sys, requests, json

jms_url = 'http://192.168.1.118/'
old_ip = sys.argv[1]
new_ip = sys.argv[2]

def get_token():
    url = jms_url + 'api/users/v1/auth/'
    query_args = {
        "username": "admin",
        "password": "admin"
    }
    response = requests.post(url, data=query_args)
    return json.loads(response.text)['token']

def update_assetsip():

    url = jms_url + 'api/assets/v1/assets/?ip=%s' %old_ip

    jms_token = get_token()

    headers = {
        'Authorization': 'Bearer ' + jms_token,
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

    data = '{ "ip": "%s", "hostname": "%s" }' %(new_ip, hostname)
    try:
        url_1 = jms_url + 'api/assets/v1/assets/%s/' %id
    except UnboundLocalError:
        print("\033[32m 资产ip输入错误 \033[0m")
        exit()

    r = requests.put(url_1, headers=headers, data=data)
    print ("\033[31m ip已经修改成{} \033[0m".format(json.loads(r.text)['ip']))
    return

try:
    update_assetsip()
except UnboundLocalError:
    print("\033[32m 资产ip输入错误 \033[0m")
    exit()
