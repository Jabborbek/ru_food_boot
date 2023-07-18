from django.contrib import admin
from .models import Category, Subcategory, Product


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']


@admin.register(Subcategory)
class AdminSubcategory(admin.ModelAdmin):
    list_display = ['category', 'name', 'created_at', 'updated_at']


@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = ['subcategory', 'name', 'description', 'price', 'status', 'image', 'created_at', 'updated_at']
