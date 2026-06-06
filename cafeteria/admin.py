from django.contrib import admin
from .models import MenuCategory, MenuItem, Order, OrderItem


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    ordering = ['order']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'stock_quantity', 'reserved_quantity', 'effective_stock']
    list_filter = ['category', 'is_available']
    list_editable = ['is_available', 'stock_quantity']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['unit_price', 'subtotal']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'status', 'total_amount', 'pickup_code', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['pickup_code', 'created_at']
