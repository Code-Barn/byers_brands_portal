"""URL configuration for Brand app."""
from django.urls import path
from . import views

app_name = 'brand'

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_redirect'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),
]
