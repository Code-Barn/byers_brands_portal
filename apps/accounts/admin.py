"""
Admin configuration for Accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .audit_models import AuditLog, SessionAudit


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'did', 'mfa_enabled', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'mfa_enabled')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'did')}),
        ('DID Document', {'fields': ('did_document',)}),
        ('MFA', {'fields': ('mfa_enabled', 'mfa_last_verified',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'username', 'did')
    ordering = ('email',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'user_did', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__email', 'user_did', 'action_details')
    readonly_fields = ('user', 'user_did', 'action', 'action_details', 'metadata',
                       'ip_address', 'user_agent', 'checksum', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(SessionAudit)
class SessionAuditAdmin(admin.ModelAdmin):
    list_display = ('user', 'did', 'ip_address', 'started_at', 'last_activity', 'is_active')
    list_filter = ('is_active', 'started_at')
    search_fields = ('user__email', 'did', 'session_key')
    readonly_fields = ('user', 'session_key', 'did', 'ip_address', 'user_agent',
                       'started_at', 'last_activity', 'ended_at', 'is_active')
    ordering = ('-last_activity',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
