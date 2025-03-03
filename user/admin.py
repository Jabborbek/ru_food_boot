from django.contrib import admin

from .models import Admin, Product, Order, \
    Address, User, SMS, Category, Measure, ProductQuantity, Dastavka_Price, Cart, OrderSale


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'create_date', 'update_date')


class AdminAdmin(admin.ModelAdmin):
    list_display = ('name', 'telegram', 'create_date', 'update_date')


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', '_type', 'quantity', 'amount', 'status', 'create_date')


class UserAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    list_display = ('id', 'fullname', 'phone', 'telegram', 'lang', 'create_date')
    list_display_links = ('fullname',)


class AddressAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    list_display = ('user', 'address', 'latitude', 'longitude',)
    list_display_links = None
    search_fields = ['user__fullname__icontains', ]


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'category', 'name', 'amount', 'time', 'birlik', 'status', 'create_date', 'update_date')

    def birlik(self, obj):
        return [measure.name for measure in obj.measure.all()]

    list_editable = ['status']


class SMSAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    list_display = ('user', 'phone', 'code', 'status')
    list_display_links = None


class OrderAdmin(admin.ModelAdmin):
    # def has_add_permission(self, request):
    #     return False

    list_display = (
        'id', 'user', 'adjusted_amount',
        'admin_status', 'create_date')

    list_display_links = ['id']
    list_filter = ['admin_status']
    search_fields = ['user__fullname__icontains', 'id']

    def adjusted_amount(self, obj):
        return obj.amount / 100

    adjusted_amount.short_description = 'Summa'


class OrderSaleAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('order', 'product', 'quantity', 'amount', 'create_date')

    list_display_links = None
    list_filter = ['create_date']
    search_fields = ['user__fullname__icontains']


class ProductQuantityInline(admin.TabularInline):
    model = ProductQuantity
    extra = 0


class ProductQuantityAdmin(admin.ModelAdmin):
    list_display = ('quantity', 'measure', 'create_date', 'update_date')


class Dastavka_PriceAdmin(admin.ModelAdmin):
    list_display = ('amount', '_from', '_to', 'create_date', 'update_date')


class MeasureAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'create_date', 'update_date')
    inlines = [ProductQuantityInline]


admin.site.register(User, UserAdmin)
admin.site.register(Measure, MeasureAdmin)
admin.site.register(Category, CategoryAdmin)
# admin.site.register(Order, OrderAdmin)
admin.site.register(OrderSale, OrderSaleAdmin)
admin.site.register(Product, ProductAdmin)
