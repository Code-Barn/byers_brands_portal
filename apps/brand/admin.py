"""Admin configuration for Brand app."""
from django.contrib import admin
from .models import BrandPage, Product


@admin.register(BrandPage)
class BrandPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_featured', 'order')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description', 'category')
