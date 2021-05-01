#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author  :   {ling}
@Time    :   2021/4/8- 14:42
'''
from django.db import models

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    is_delete = models.BooleanField(default=False,verbose_name='删除标记')

    class Meta:
        abstract = True