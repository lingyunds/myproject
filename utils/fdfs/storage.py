#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author  :   {ling}
@Time    :   2021/4/23- 20:23
'''

from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client,get_tracker_conf


class FDFSStorage(Storage):
    def __init__(self, client_conf=None, base_url=None):
        '''初始化'''
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        pass

    def _save(self,name,content):
        print(1)
        conf = get_tracker_conf(self.client_conf)
        client = Fdfs_client(conf)
        result = client.upload_by_buffer(content.read())

        # dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }

        if result.get('Status') != 'Upload successed.':
            raise Exception('上传文件到FastDFS失败')
        filename = result.get('Remote file_id')
        return filename.decode()

    def exists(self, name):
        return False

    def url(self, name):
        return self.base_url+name