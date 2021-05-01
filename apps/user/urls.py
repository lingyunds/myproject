#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author  :   {ling}
@Time    :   2021/4/8- 14:34
'''
from django.urls import re_path
from apps.user.views import Register,Active,Login,Logout,UserInfo,UserOrder,UserAddress


urlpatterns = [
        re_path('^register/$',Register.as_view(),name='register'),
        re_path('^active/(?P<token>.*)/$',Active.as_view(),name='active'),
        re_path('^login/$',Login.as_view(),name='login'),
        re_path('^logout/$',Logout.as_view(),name='logout'),
        re_path('^$',UserInfo.as_view(),name='user'),
        re_path('^order/(?P<page>\d+)/$',UserOrder.as_view(),name='order'),
        re_path('^address/$',UserAddress.as_view(),name='address'),
        ]
