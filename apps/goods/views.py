from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from django.core.cache import cache
from django.core.paginator import Paginator
from apps.goods.models import GoodsSKU,IndexGoodsBanner,IndexPromotionBanner,GoodsType,IndexTypeGoodsBanner
from apps.order.models import OrderGoods
# Create your views here.
class Index(View):
    def get(self,request):
        #获取缓存
        context = cache.get('index_data')
        if context is None:
            #首页商品种类
            types = GoodsType.objects.all()
            #首页轮播商品
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')
            #首页轮播活动商品
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
            #首页分类商品
            for type in types:
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by('index')
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=0).order_by('index')

                type.image_banners = image_banners
                type.title_banners = title_banners

            context = {'types':types,
                       'goods_banners':goods_banners,
                       'promotion_banners':promotion_banners,
                       }
            #没有缓存则设置缓存
            cache.set('index_data',context,3600)

        #获取购物车条目数
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)

        context.update(cart_count=cart_count)

        return render(request,'index.html',context)


class Detail(View):
    def get(self,request,sku_id):
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))

        types = GoodsType.objects.all()
        spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=sku_id)
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]
        sku_comments = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        user = request.user
        sku_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            conn = get_redis_connection('default')
            history_key = 'history_%d'%user.id
            conn.lrem(history_key,0,sku_id)
            conn.lpush(history_key,sku_id)
            conn.ltrim(history_key,0,4)

        context = {'sku':sku,
                   'types':types,
                   'spu_skus':spu_skus,
                   'new_skus':new_skus,
                   'sku_comments':sku_comments,
                   'cart_count':cart_count
        }
        return render(request,'detail.html',context)


# /list?type_id=种类id&page=页码&sort=排序方式
# /list/种类id/页码/排序方式
# /list/种类id/页码?sort=排序方式
class List(View):
    def get(self,request,type_id,page):
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))

        types = GoodsType.objects.all()

        #设置排序方式
        sort = request.GET.get('sort')
        if sort == 'price':
            order_by = 'price'
        elif sort == 'hot':
            order_by = '-sales'
        else:
            sort = 'default'
            order_by = '-id'
        skus = GoodsSKU.objects.filter(type=type).order_by('%s'%order_by)

        #对内容分页
        paginator = Paginator(skus,1)

        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1
        #获取分页内容
        page_skus = paginator.page(page)

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

        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        context = {'type':type,
                   'types':types,
                   'page_skus':page_skus,
                   'new_skus': new_skus,
                   'cart_count':cart_count,
                   'sort':sort,
                   'pages':pages,
        }

        return render(request,'list.html',context)