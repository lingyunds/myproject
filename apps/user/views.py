from django.shortcuts import render,redirect
from django.views import View
from django.urls import reverse
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_redis import get_redis_connection
from django.core.paginator import Paginator
from itsdangerous import TimedJSONWebSignatureSerializer as danger
from itsdangerous import SignatureExpired
from apps.user.my_form import RegisterForm,LoginForm,AddressForm
from apps.user.models import User,Address
from apps.goods.models import GoodsSKU
from apps.order.models import OrderInfo,OrderGoods
from celery_tasks.tasks import send_register_mail

# Create your views here.


class Register(View):
    def get(self,request):
        form = RegisterForm()
        return render(request, 'register.html', {'form':form})

    def post(self,request):
        form = RegisterForm(request.POST)
        #验证表单数据有效性
        if form.is_valid():
            data = form.cleaned_data
            #创建普通用户，默认is_active=1，需更改
            user = User.objects.create_user(username=data['username'],email=data['email'],password=data['password'],is_active=0)
            #设置加密
            salt = danger(settings.SECRET_KEY,3600)
            info = {'confirm':user.id}
            token = salt.dumps(info)
            token = token.decode()
            #调用异步celery发送邮件，并另开一个celery处理者:celery -A celery_task.tasks worker -l info 可在其它机器
            send_register_mail.delay(data['email'],data['username'],token)

            return redirect(reverse('goods:index'))
        else:
            clean_errors = form.errors.get('__all__')
            return render(request, 'register.html', {'form':form, 'clean_errors':clean_errors})


class Active(View):
    def get(self,request,token):
        #解密数据，需与加密相同参数
        salt = danger(settings.SECRET_KEY,3600)
        try:
            info = salt.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return e


class Login(View):
    def get(self,request):
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checkbox = 'True'
            form = LoginForm({'username':username,'checkbox':checkbox})
        else:
            form = LoginForm()
        return render(request,'login.html',{'form':form})

    def post(self,request):
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            #保存经过验证的用户session
            auth.login(request,data[1])
            #获取跳转到登录页前的地址
            next_url = request.GET.get('next',reverse('goods:index'))
            response = redirect(next_url)
            #判断是否记住我并操作cookies
            remember = data[0]['checkbox']
            if remember == 'True':
                response.set_cookie('username',data[0]['username'],max_age=7*24*3600)
            else:
                response.delete_cookie('username')
            return response
        else:
            clean_errors = form.errors.get('__all__')
            return render(request, 'login.html', {'form':form, 'clean_errors':clean_errors})


class Logout(View):
    def get(self,request):
        auth.logout(request)
        return redirect(reverse('goods:index'))


@method_decorator(login_required,name='get')
class UserInfo(View):
    def get(self,request):
        user = request.user
        address = Address.objects.get_default_address(user)

        con = get_redis_connection('default')
        #获取用户历史记录
        history_key = 'history_%d'%user.id
        sku_ids = con.lrange(history_key,0,4)

        skus = []
        for id in sku_ids:
            sku = GoodsSKU.objects.get(id=id)
            skus.append(sku)

        page = 'user'

        context = {'address':address,
                   'skus':skus,
                   'page':page}

        return render(request,'user_center_info.html',context)


@method_decorator(login_required,name='get')
class UserOrder(View):
    def get(self,request,page):
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        for order in orders:
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            for order_sku in order_skus:
                amount = order_sku.count*order_sku.price
                order_sku.amount = amount

            #订单状态
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            #订单内商品
            order.order_skus = order_skus

        paginator = Paginator(orders,1)

        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        order_page = paginator.page(page)

        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        context = {'order_page': order_page,
                   'pages': pages,
                   'page': 'order'}

        return render(request,'user_center_order.html',context)


@method_decorator(login_required,name='get')
class UserAddress(View):
    def get(self,request):
        form = AddressForm()
        user = request.user
        address = Address.objects.get_default_address(user)
        page = 'address'

        context = {'form':form,
                   'address':address,
                   'page':page
        }

        return render(request,'user_center_site.html',context)

    def post(self,request):
        form = AddressForm(request.POST)
        user = request.user
        address = Address.objects.get_default_address(user)
        if form.is_valid():
            data = form.cleaned_data
            if address:
                is_default = False
            else:
                is_default = True
            Address.objects.create(user=user,
                                   receiver=data['receiver'],
                                   addr=data['addr'],
                                   zip_code=data['zip_code'],
                                   phone=data['phone'],
                                   is_default=is_default)
            return redirect(reverse('user:address'))
        else:

            return render(request,'user_center_site.html',{'form':form,'address':address})









