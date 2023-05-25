from django.contrib import admin
from .models import Coupon, Order, OrderedProduct

# Register your models here.
admin.site.register(Coupon)

class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    readonly_fields = ['title', 'count', 'price', 'size', 'color']
    extra = 0
    
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderedProductInline]
