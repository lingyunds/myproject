#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author  :   {ling}
@Time    :   2021/4/8- 14:34
'''
from django.urls import re_path
from apps.order.views import OrderPlace,OrederCommit,OrderPay,CheckPay,Comment
urlpatterns = [
    re_path('^place/$',OrderPlace.as_view(),name='place'),
    re_path('^commit/$',OrederCommit.as_view(),name='commit'),
    re_path('^pay/$',OrderPay.as_view(),name='pay'),
    re_path('^check',CheckPay.as_view(),name='check'),
    re_path('^comment/(?P<order_id>.+)$', Comment.as_view(), name='comment'),
]