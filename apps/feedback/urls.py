"""
URL configuration for Feedback app.
"""
from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_form, name='submit'),
    path('submit/', views.submit_feedback, name='submit'),
    path('success/', views.feedback_success, name='success'),
    path('list/', views.feedback_list, name='list'),
    path('<int:feedback_id>/', views.feedback_detail, name='detail'),
    path('<int:feedback_id>/update/', views.feedback_update_status, name='update_status'),
]