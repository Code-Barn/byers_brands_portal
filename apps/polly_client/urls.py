"""
URL configuration for Polly Client app.
"""
from django.urls import path
from . import views

app_name = 'polly_client'

urlpatterns = [
    # Views
    path('polls/', views.polls_view, name='polls'),
    path('polls/<int:poll_id>/', views.poll_detail_view, name='poll_detail'),

    # API endpoints
    path('api/polls/', views.api_polls, name='api_polls'),
    path('api/polls/<int:poll_id>/', views.api_poll_detail, name='api_poll_detail'),
    path('api/vote/', views.api_vote, name='api_vote'),
    path('api/health/', views.api_health, name='api_health'),
]