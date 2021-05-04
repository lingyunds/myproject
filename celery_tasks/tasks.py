#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author  :   {ling}
@Time    :   2021/4/10- 10:45
'''

from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
import os

# 在任务处理者一端加这几句
# import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from apps.goods.models import IndexGoodsBanner,IndexPromotionBanner,GoodsType,IndexTypeGoodsBanner

#创建对象并指定任务中间人
app = Celery('celery_tasks.tasks',broker='redis://:123456@117.173.79.125:6379/2')

@app.task
def send_register_mail(email,username,token):
    subject = '天狼世佳账户激活'
    message = ''
    sender = settings.EMAIL_FROM
    #收件人需要为列表
    receiver = [email]
    html_message = '<h1>%s欢迎成为会员</h1>点击下方链接激活账户<br><a href="http://192.168.2.105:80/user/active/%s">http://192.168.2.105:80/user/active/%s</a>'%(username,token,token)
    #调用发送内置发送邮件函数,setting配置smtp邮箱
    send_mail(subject,message,sender,receiver,html_message=html_message)


@app.task
def generate_static_index():
    types = GoodsType.objects.all()

    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    for type in types:
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        type.image_banners = image_banners
        type.title_banners = title_banners


    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners,
               }
    #生成静态文件
    temp = loader.get_template('static_index.html')
    static_index_html = temp.render(context)
    save_path = os.path.join(settings.BASE_DIR,'collection/index.html')
    with open(save_path,'w') as f:
        f.write(static_index_html)

