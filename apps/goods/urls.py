#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author  :   {ling}
@Time    :   2021/4/8- 14:34
'''
from django.urls import re_path
from apps.goods.views import Index,Detail,List
urlpatterns = [
    re_path('^index/$',Index.as_view(),name='index'),
    re_path('^goods/(?P<sku_id>\d+)/$',Detail.as_view(),name='detail'),
    re_path('^list/(?P<type_id>\d+)/(?P<page>\d+)/$',List.as_view(),name='list'),
    re_path('^$',Index.as_view()),
]