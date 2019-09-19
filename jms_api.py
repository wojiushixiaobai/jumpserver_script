#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, requests, json, uuid, sys, datetime, time, random

# jumpserver url 地址
jms_url                = 'http://192.168.1.118'

# 管理员账户
users_username         = 'admin'
users_password         = 'admin'

# 资产管理用户
assets_admin_name      = 'root_test'
assets_admin_username  = 'root'
assets_admin_password  = 'root'

# 资产系统用户
assets_system_name     = 'update_user'
# assets_system_username = 'test_user'

class HTTP:
    server = None
    token = None

    @classmethod
    def get_token(cls, username, password):
        print("获取Token")
        data      = {'username': username, 'password': password}
        url       = "/api/authentication/v1/auth/"
        res       = requests.post(cls.server + url, data)
        res_data  = res.json()
        token     = res_data.get('token')
        cls.token = token

    @classmethod
    def get(cls, url, params=None, **kwargs):
        url               = cls.server + url
        headers           = {
            'Authorization': "Bearer {}".format(cls.token)
        }
        kwargs['headers'] = headers
        res               = requests.get(url, params, **kwargs)
        return res

    @classmethod
    def post(cls, url, data=None, json=None, **kwargs):
        url               = cls.server + url
        headers           = {
            'Authorization': "Bearer {}".format(cls.token)
        }
        kwargs['headers'] = headers
        res               = requests.post(url, data, json, **kwargs)
        return res

class User(object):

    def __init__(self):
        self.id           = None
        self.username     = None
        self.email_suffix = 'jumpserver.org'

    def input_preconditions(self):
        print("请输入前置条件: ")
        self.username     = input("Please enter user username: ")
        self.useremail    = input("Please enter user email (user@jumpserver.org): ")

    def get_preconditions(self):
        self.input_preconditions()

    def exist(self):
        print("校验用户")
        url               = '/api/users/v1/users/'
        params            = {'username': self.username}
        res               = HTTP.get(url, params=params)
        res_data          = res.json()
        if res.status_code in [200, 201] and res_data:
            self.id       = res_data[0].get('id')
            return True
        print("用户不存在: {}".format(self.username))
        return False

    def create(self):
        print("创建用户")
        url               = '/api/users/v1/users/'
        data              = {
            'name': self.username,
            'username': self.username,
            'email': self.useremail,
            'is_active': True
        }
        res               = HTTP.post(url, data)
        self.id           = res.json().get('id')

    def perform(self):
        self.get_preconditions()
        if self.exist():
            return
        self.create()

class Node(object):

    def __init__(self):
        self.id           = None
        self.name         = None

    def input_preconditions(self):
        self.name         = input("Please enter node name: ")

    def get_preconditions(self):
        self.input_preconditions()

    def exist(self):
        print("校验资产节点")
        url               = '/api/assets/v1/nodes/'
        params            = {'value': self.name}
        res               = HTTP.get(url, params=params)
        res_data          = res.json()
        if res.status_code in [200, 201] and res_data:
            self.id       = res_data[0].get('id')
            return True
        print('节点不存在: {}'.format(self.id))
        return False

    def create(self):
        print("创建资产节点")
        url               = '/api/assets/v1/nodes/'
        data              = {
            'value': self.name
        }
        res               = HTTP.post(url, data)
        self.id           = res.json().get('id')

    def perform(self):
        self.get_preconditions()
        if self.exist():
            return
        self.create()

class AdminUser(object):

    def __init__(self):
        self.id           = None
        self.name         = assets_admin_name
        self.username     = assets_admin_username
        self.password     = assets_admin_password

    def input_preconditions(self):
        if self.name is None:
            self.name = input("Please enter assets admin name: ")
        if self.username is None:
            self.username = input("Please enter assets admin username: ")
        if self.password is None:
            self.password     = input("Please enter assets admin password: ")

    def get_preconditions(self):
        self.input_preconditions()

    def exist(self):
        print("校验管理用户")
        url               = '/api/assets/v1/admin-user/'
        params            = {'username': self.name}
        res               = HTTP.get(url, params=params)
        res_data          = res.json()
        if res.status_code in [200, 201] and res_data:
            self.id       = res_data[0].get('id')
            return True
        print("管理用户不存在: {}".format(self.id))
        return False

    def create(self):
        print("创建管理用户")
        url               = '/api/users/v1/users/'
        data              = {
            'name': self.name,
            'username': self.username,
            'password': self.password
        }
        res               = HTTP.post(url, data)
        self.id           = res.json().get('id')

    def perform(self):
        self.get_preconditions()
        if self.exist():
            return
        self.create()

class Asset(object):

    def __init__(self):
        self.id = None
        self.ip = None
        self.admin_user = AdminUser()
        self.node = Node()

    def input_preconditions(self):
        self.ip = input("Please enter asset ip: ")

    def get_preconditions(self):
        self.input_preconditions()
        self.admin_user.get_preconditions()
        self.node.get_preconditions()

    def exist(self):
        print("校验资产")
        url = '/api/assets/v1/assets/'
        params = {
            'ip': self.ip
        }
        res = HTTP.get(url, params)
        res_data = res.json()
        if res.status_code in [200, 201] and res_data:
            self.id = res_data[0].get('id')
            return True
        print("资产不存在: {}".format(self.ip))
        return False

    def create(self):
        print("创建资产")
        self.admin_user.perform()
        self.node.perform()
        url = '/api/assets/v1/assets/'
        data = {
            'hostname': self.ip,
            'ip': self.ip,
            'admin_user': self.admin_user.id,
            'nodes': [self.node.id],
            'is_active': True
        }
        res = HTTP.post(url, data)
        self.id = res.json().get('id')

    def perform(self):
        self.get_preconditions()
        if not self.exist():
            self.create()

class SystemUser(object):

    def __init__(self):
        self.id       = None
        self.name     = assets_system_name
        # self.username = assets_system_username

    def input_preconditions(self):
        if self.name is None:
            self.rname = input("Please enter assets admin name: ")

    def get_preconditions(self):
        self.input_preconditions()

    def exist(self):
        print("校验系统用户")
        url = '/api/assets/v1/system-user/'
        params = {'name': self.name}
        res = HTTP.get(url, params)
        res_data = res.json()
        if res.status_code in [200, 201] and res_data:
            self.id = res_data[0].get('id')
            return True
        print("系统用户不存在: {}".format(self.id))
        return False

    # def create(self):
        # print("创建系统用户")
        # url = '/api/assets/v1/system-user/'
        # data = {
            # 'name': self.username,
            # 'is_active': 'true',
            # 'username': self.username,
            # 'email': '{}@{}'.format(self.username, self.email_suffix),
            # 'is_active': True
        # }
        # res = HTTP.post(url, data)
        # self.id = res.json().get('id')

    def perform(self):
        self.get_preconditions()
        if self.exist():
            return
        sys.exit()

class AssetPermission(object):

    def __init__(self):
        self.name_prefix = None
        self.name_suffix = self.get_name_suffix()
        if self.name_prefix is not None:
            self.name = '{}_{}'.format(self.name_prefix, self.name_suffix)
        self.user = User()
        self.asset = Asset()
        self.system_user = SystemUser()

    @staticmethod
    def get_name_suffix():
        name_suffix_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
        name_suffix_uuid = str(uuid.uuid4().hex[:6])
        name_suffix = "{}_{}".format(name_suffix_time, name_suffix_uuid)
        return name_suffix

    def input_preconditions(self):
        self.name = input("Please enter asset permission name: ")

    def get_preconditions(self):
        self.input_preconditions()

    def create(self):
        print("创建资产授权规则")
        url = '/api/perms/v1/asset-permissions/'
        data = {
            'name': self.name,
            'users': [self.user.id],
            'assets': [self.asset.id],
            'system_users': [self.system_user.id],
            'actions': ['all'],
            'is_active': True
        }
        print("data: ")
        print(data)
        res = HTTP.post(url, data)
        res_data = res.json()
        if res.status_code in [200, 201]:
            print("response: ")
            print(res_data)
            print("创建资产授权规则成功")
        else:
            print("response: ")
            print(res_data)
            print("创建授权规则失败")

    def perform(self):
        self.user.perform()
        self.asset.perform()
        self.system_user.perform()
        self.get_preconditions()
        self.create()

class APICreateAssetPermission(object):

    def __init__(self):
        self.jms_url = jms_url
        self.superuser_username = users_username
        self.superuser_password = users_password
        self.token = None
        self.server = None
        self.perm = AssetPermission()

    def init_http(self):
        HTTP.server = self.jms_url
        HTTP.get_token(self.superuser_username, self.superuser_password)

    def perform(self):
        self.init_http()
        self.perm.perform()

if __name__ == '__main__':

    api = APICreateAssetPermission()
    api.perform()
