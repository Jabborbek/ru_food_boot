from django.contrib import admin
from .models import Category, Product, User


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = ['id', 'telegram', 'lang', 'created_at', ]


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']


@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = ['id', 'category', 'name', 'description', 'price', 'status',]
    list_editable = ['status', 'price', ]
