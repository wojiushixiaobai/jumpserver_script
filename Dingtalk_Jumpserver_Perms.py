#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 添加了判断，只有状态是通过且完成的审批才会添加相应的授权，适合 Jumpserver 1.5.2 版本
# Usage: python Dingtalk_Jumpserver_Perms.py
#

import os, requests, json, sys, datetime, time, random, smtplib, shutil

# Jumpserver
jms_url      = 'http://192.168.1.118/'
username     = 'admin'
password     = 'admin'

# Dingtalk
appkey       = 'dingxxxxxxxxxx'
appsecret    = '0GrL-xxxxxxxxxxxx'
process_code = 'PROC-xxxxxxxxxxxxxxx'

# 打印颜色
colour = ('31', '32', '33', '34', '35', '36', '37')

# 生成颜色随机数
def getNums():
    return random.randint(0, 6)

# ISO 8601时间
def isoformat(time):
    if isinstance(time, datetime.datetime):
        return time.isoformat();
    elif isinstance(time, datetime.timedelta):
        hours = time.seconds // 3600
        minutes = time.seconds % 3600 // 60
        seconds = time.seconds % 3600 % 60
        return 'P%sDT%sH%sM%sS' % (time.days, hours, minutes, seconds)

# 获取 Jumpserver token
def get_JmsToken():
    url = jms_url + 'api/users/v1/auth/'
    query_args = {
        'username': username,
        'password': password
    }
    response = requests.post(url, data=query_args)
    return json.loads(response.text)['token']

# 获取 Jumpserver 用户id
def get_JmsUserId(username):
    jms_token    = get_JmsToken()
    url          = jms_url + 'api/users/v1/users/?name=%s' %username
    headers      = {
        'Authorization': 'Bearer ' + jms_token,
        'accept'       : 'application/json'
    }
    response = requests.get(url, headers=headers)
    return json.loads(response.text)[0]['id']

# 获取 Jumpserver 资产id
def get_JmsAssetsId(assetsip):
    jms_token    = get_JmsToken()
    url = jms_url + 'api/assets/v1/assets/?ip=%s' %assetsip
    headers = {
        'Authorization': 'Bearer ' + jms_token,
        'accept'       : 'application/json'
    }
    response  = requests.get(url, headers=headers)
    return json.loads(response.text)[0]['id']

# 获取 Jumpserver 系统用户id
def get_JmsSystemuserId(systemusername):
    jms_token    = get_JmsToken()
    url = jms_url + 'api/assets/v1/system-user/?name=%s' %systemusername
    headers = {
        'Authorization': 'Bearer ' + jms_token,
        'accept'       : 'application/json'
    }
    response  = requests.get(url, headers=headers)
    return json.loads(response.text)[0]['id']

# 获取 钉钉 token
def get_DingtalkToken():
    headers      = {
        'Content-Type': 'application/json'
    }
    url          = 'https://oapi.dingtalk.com/gettoken?appkey=%s&appsecret=%s' %(appkey, appsecret)
    response     = requests.get(url, headers=headers)
    return json.loads(response.text)['access_token']

# 开始时间设置为 7 天前 9:00:00
def getTime():
    beginDate    = datetime.datetime.now()
    yes_time     = beginDate + datetime.timedelta(days=+1)
    aWeekDelta   = datetime.timedelta(weeks=1)
    aWeekAgo     = yes_time - aWeekDelta
    begin        = aWeekAgo.strftime("%Y-%m-%d 09:00:00")
    return int(time.mktime(time.strptime('%s' %begin, '%Y-%m-%d %H:%M:%S')))

# 获取审批单号
def get_DingtalkProcess():
    access_token = get_DingtalkToken()
    start_time   = getTime()
    url          = 'https://oapi.dingtalk.com/topapi/processinstance/listids?access_token=%s' %access_token
    headers      = {
        'Content-Type': 'application/json'
    }
    data         = '{ "process_code": "%s", "start_time": "%s"}' %(process_code, start_time)
    response     = requests.post(url, headers=headers, data=data)
    if json.loads(response.text)["errcode"] == 0:
        return json.loads(response.text)["result"]["list"]

# 过滤需要的审批单号
def get_DingtalkProcessInstance():
    access_token           = get_DingtalkToken()
    process_instance       = get_DingtalkProcess()
    x                      = len(process_instance)
    i                      = 0
    process_id             = []
    url                    = 'https://oapi.dingtalk.com/topapi/processinstance/get?access_token=%s' %access_token
    headers                = {
        'Content-Type': 'application/json'
    }
    while i < x:
        process_instance_id = process_instance[i]
        data  = '{ "process_instance_id": "%s" }' %process_instance_id
        response = requests.post(url, headers=headers, data=data)
        if json.loads(response.text)["errcode"] == 0:
            if json.loads(response.text)["process_instance"]["status"] == "COMPLETED":
                if json.loads(response.text)["process_instance"]["result"] == "agree":
                    process_id.append(process_instance_id)

        i += 1

    try:
        return process_id
    except SyntaxError:
        exit()

# 处理审批
def create_JmsPerms():
    access_token           = get_DingtalkToken()
    process_instance       = get_DingtalkProcessInstance()
    url                    = 'https://oapi.dingtalk.com/topapi/processinstance/get?access_token=%s' %access_token
    headers                = {
        'Content-Type': 'application/json'
    }
    x                      = len(process_instance)
    i                      = 0
    while i < x:
        data               = {
            'process_instance_id': process_instance[i]
        }
        response           = requests.post(url, headers=headers, data=json.dumps(data))
        i                 += 1

        perms_name         = json.loads(response.text)["process_instance"]["business_id"]
        perms_user         = json.loads(response.text)["process_instance"]["form_component_values"][1]["value"]
        perms_assets       = json.loads(response.text)["process_instance"]["form_component_values"][2]["value"]
        perms_system_user  = json.loads(response.text)["process_instance"]["form_component_values"][3]["value"]
        perms_date         = json.loads(response.text)["process_instance"]["form_component_values"][4]["value"]
        perms_comment      = json.loads(response.text)["process_instance"]["form_component_values"][5]["value"]

        perms_assets_list  = json.loads(perms_assets)

        begin_date         = json.loads(perms_date)[0]
        perms_begin_date   = isoformat(datetime.datetime.strptime(begin_date, "%Y-%m-%d %H:%M"))

        end_date           = json.loads(perms_date)[1]
        perms_end_date     = isoformat(datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M"))

        user_name          = eval(repr(perms_user).replace('\\x','%')).upper()
        perms_username_id  = get_JmsUserId(user_name)

        perms_assets_id    = []
        if len(perms_assets_list) == 1 :
            assets_ip      = perms_assets_list[0]
            assets_id      = get_JmsAssetsId(assets_ip)
            perms_assets_id.append(assets_id)

        elif len(perms_assets_list) > 1 :
            assets_x       = len(perms_assets_list)
            assets_i       = 0
            while assets_i < assets_x:
                assets_ip  = perms_assets_list[assets_i]
                assets_id  = get_JmsAssetsId(assets_ip)
                perms_assets_id.append(assets_id)
                assets_i  += 1

        perms_system_id    = get_JmsSystemuserId(perms_system_user)

        url_1              = jms_url + 'api/perms/v1/asset-permissions/'
        jms_token          = get_JmsToken()
        headers            = {
            'Authorization': 'Bearer ' + jms_token,
            'accept'       : 'application/json',
            'Content-Type' : 'application/json'
        }
        data               = {
            'actions': [ 'all' ],
            'name': perms_name,
            'is_active': 'true',
            'date_start': perms_begin_date,
            'date_expired': perms_end_date,
            'comment': perms_comment,
            'users': [perms_username_id],
            'user_groups': [],
            'assets': perms_assets_id,
            'nodes': [],
            'system_users': [perms_system_id]
        }

        r                  = requests.post(url_1, headers=headers, data=json.dumps(data))
        if u"字段必须唯一" in json.loads(r.text)["name"]:
            nums           = getNums()
            print("\033[{}m {} 该授权名称已经存在, 跳过 \033[0m") .format(colour[nums], perms_name)

create_JmsPerms()
