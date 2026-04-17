"""Views for Brand app."""
from django.shortcuts import render
from django.conf import settings
from .models import BrandPage, Product


def home(request):
    """Home page view."""
    featured_products = Product.objects.filter(is_featured=True).order_by('order')[:4]
    return render(request, 'brand/home.html', {
        'page': 'home',
        'featured_products': featured_products,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


def about(request):
    """About Us page view."""
    return render(request, 'brand/about.html', {
        'page': 'about',
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


def products(request):
    """Products page view."""
    products = Product.objects.filter(is_featured=False).order_by('order', 'name')
    featured_products = Product.objects.filter(is_featured=True).order_by('order')
    categories = Product.objects.values_list('category', flat=True).distinct()
    return render(request, 'brand/products.html', {
        'page': 'products',
        'products': products,
        'featured_products': featured_products,
        'categories': categories,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


def contact(request):
    """Contact page view."""
    return render(request, 'brand/contact.html', {
        'page': 'contact',
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })


def product_detail(request, product_id):
    """Product detail page view."""
    product = Product.objects.get(id=product_id)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product_id).order_by('order')[:4]
    return render(request, 'brand/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'brand_color': getattr(settings, 'BRAND_COLOR', '#0064aa')
    })
