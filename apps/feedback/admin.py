"""
Admin configuration for Feedback app.
"""
from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('subject', 'message', 'user__email')
    readonly_fields = ('user', 'subject', 'message', 'screenshot', 'url_context', 'created_at', 'updated_at')
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Content', {'fields': ('subject', 'message', 'category', 'screenshot', 'url_context')}),
        ('Status', {'fields': ('status', 'admin_notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    ordering = ('-created_at',)