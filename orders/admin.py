from django.contrib import admin
from .models import Payment,Order,OrderProduct, ProductGallery
import admin_thumbnails

# Register your models here.

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0
    inlines = [ProductGalleryInline]

class OrderAdmin(admin.ModelAdmin):
    list_display   = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter    = ['status', 'is_ordered']
    search_fields  = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_pera_page = 20
    inlines        = [OrderProductInline]


admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)
admin.site.register(ProductGallery)
