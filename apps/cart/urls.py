#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author  :   {ling}
@Time    :   2021/4/8- 14:34
'''
from django.urls import re_path
from apps.cart.views import CartAdd,CartInfo,CartUpdate,CartDelete

urlpatterns = [
    re_path('^add/$',CartAdd.as_view(),name='add'),
    re_path('^$',CartInfo.as_view(),name='cart'),
    re_path('^update/$',CartUpdate.as_view(),name='update'),
    re_path('^delete/$',CartDelete.as_view(),name='delete')
]