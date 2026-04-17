"""
URL configuration for Accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('did-login/', views.did_login, name='did_login'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    
    # Investor Dashboard (placeholder)
    path('dashboard/', views.investor_dashboard, name='investor_dashboard'),
    path('', views.investor_dashboard, name='investor_home'),
    
    # API endpoints
    path('api/generate-did/', views.api_generate_did, name='api_generate_did'),
    path('api/verify-vc/', views.api_verify_vc, name='api_verify_vc'),
    path('api/challenge/', views.generate_challenge, name='generate_challenge'),
]
