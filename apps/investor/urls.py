"""
URL configuration for Investor app.
"""
from django.urls import path
from . import views

app_name = 'investor'

urlpatterns = [
    # Main dashboard
    path('', views.investor_dashboard, name='dashboard'),

    # Portfolio
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('documents/', views.documents_view, name='documents'),
    path('opportunities/', views.opportunities_view, name='opportunities'),
    path('roi-calculator/', views.roi_calculator, name='roi_calculator'),

    # Document actions
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/<int:document_id>/download/', views.download_document, name='download_document'),
    path('documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),

    # API endpoints
    path('api/investments/', views.api_investments, name='api_investments'),
    path('api/portfolio/', views.api_portfolio, name='api_portfolio'),
    path('api/portfolio/summary/', views.api_portfolio_summary, name='api_portfolio_summary'),
    path('api/documents/', views.api_documents, name='api_documents'),
    path('api/documents/<int:document_id>/', views.api_delete_document, name='api_delete_document'),
    path('api/opportunities/', views.api_opportunities, name='api_opportunities'),
]