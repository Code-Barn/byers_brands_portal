"""
Django admin configuration for Investor app.
"""
from django.contrib import admin
from .models import Investment, Portfolio, Document, InvestmentOpportunity


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'amount', 'current_value', 'status', 'created_at']
    list_filter = ['status', 'date_invested']
    search_fields = ['name', 'user__email']
    date_hierarchy = 'created_at'


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_value', 'total_invested', 'total_returns', 'last_updated']
    search_fields = ['user__email']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'document_type', 'file_size', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title', 'user__email']
    date_hierarchy = 'uploaded_at'


@admin.register(InvestmentOpportunity)
class InvestmentOpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'min_investment', 'expected_returns_percentage', 'status', 'deadline']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'