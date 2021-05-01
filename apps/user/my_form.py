#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author  :   {ling}
@Time    :   2021/4/8- 19:24
'''
from django import forms
from django.core.exceptions import ValidationError
from apps.user.models import User
from django.contrib import auth
import re


class RegisterForm(forms.Form):
    username = forms.CharField(min_length=4,error_messages={'min_length':'用户名太短了','required':'字段不能为空'})
    email = forms.EmailField(error_messages={'required':'请输入邮箱'})
    password = forms.CharField(min_length=6,max_length=16,widget=forms.PasswordInput,error_messages={'min_length':'密码太短了','max_length':'密码过长','required':'请输入密码'})
    r_password = forms.CharField(min_length=6,max_length=16,widget=forms.PasswordInput)

    #局部钩子
    def clean_username(self):
        val = self.cleaned_data.get('username')
        if val.isdigit():
            raise ValidationError('用户名不能是纯数字')
        elif User.objects.filter(username=val).first():
            raise ValidationError('用户名已存在')
        else:
            return val

    def clean_email(self):
        val = self.cleaned_data.get('email')
        if User.objects.filter(email=val).first():
            raise ValidationError('邮箱已被注册')
        else:
            return val

    #全局钩子
    def clean(self):
        val = self.cleaned_data.get('password')
        r_val = self.cleaned_data.get('r_password')
        if val == r_val:
            #返回所有有效数据
            return self.cleaned_data
        else:
            raise ValidationError('两次输入不一致')


class LoginForm(forms.Form):
    username = forms.CharField(min_length=4,error_messages={'required':'请输入用户名'})
    password = forms.CharField(min_length=6,max_length=16,widget=forms.PasswordInput)
    checkbox = forms.CharField(widget=forms.CheckboxInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = User.objects.filter(username=username).first()
        if user is not None:
            if user.is_active == 1:
                return username
            else:
                raise ValidationError('用户未激活')
        else:
            raise ValidationError('用户名不存在')


    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = auth.authenticate(username=username,password=password)
        if username is not None and user is None:
            raise ValidationError('密码错误，请重新输入')
        else:
            #视图要用到user对象，需传出
            return self.cleaned_data,user


class AddressForm(forms.Form):
    receiver = forms.CharField(min_length=2,error_messages={'required':'请填写收件人'})
    addr =  forms.CharField(widget=forms.Textarea(attrs={'style':'resize:none;height:90px;width:300px;border:1px solid #D3D3D3'}))
    zip_code = forms.CharField(max_length=6)
    phone = forms.CharField()

    def clean_addr(self):
        addr = self.cleaned_data.get('addr')
        if addr is None:
            raise ValidationError('请输入收货地址')
        elif len(addr) < 15:
            raise ValidationError('请输入更详细信息')
        else:
            return addr

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^1[3|4|5|7|8|9][0-9]{9}$',phone):
            raise ValidationError('请输入正确的电话号码')
        else:
            return phone

