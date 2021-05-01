from django.contrib import admin
from django.core.cache import cache
from apps.goods.models import GoodsSKU,IndexGoodsBanner,IndexPromotionBanner,GoodsType,IndexTypeGoodsBanner

# Register your models here.
class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        from celery_tasks.tasks import generate_static_index
        generate_static_index.delay()

        cache.delete('index_data')


    def delete_model(self, request, obj):
        super().delete_model(request, obj)

        from celery_tasks.tasks import generate_static_index
        generate_static_index.delay()

        cache.delete('index_data')

class GoodsSKUAdmin(BaseModelAdmin):
    pass


class GoodsTypeAdmin(BaseModelAdmin):
    pass


class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass

admin.site.register(GoodsSKU,GoodsSKUAdmin)
admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)