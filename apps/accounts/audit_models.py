"""
Audit logging models for DID operations.
"""
import hashlib
import json
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class AuditLog(models.Model):
    """
    Immutable audit log for DID operations.
    Records all authentication and credential actions for security and compliance.
    """

    class ActionType(models.TextChoices):
        # Authentication actions
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'
        LOGIN_FAILED = 'login_failed', 'Login Failed'
        DID_LOGIN = 'did_login', 'DID Login'
        DID_LOGIN_FAILED = 'did_login_failed', 'DID Login Failed'

        # MFA actions
        MFA_ENABLED = 'mfa_enabled', 'MFA Enabled'
        MFA_DISABLED = 'mfa_disabled', 'MFA Disabled'
        MFA_VERIFIED = 'mfa_verified', 'MFA Verified'
        MFA_VERIFICATION_FAILED = 'mfa_verification_failed', 'MFA Verification Failed'
        MFA_BACKUP_USED = 'mfa_backup_used', 'MFA Backup Code Used'

        # Registration actions
        REGISTER = 'register', 'Registration'
        DID_GENERATED = 'did_generated', 'DID Generated'

        # Credential actions
        VC_ISSUED = 'vc_issued', 'Verifiable Credential Issued'
        VC_VERIFIED = 'vc_verified', 'Verifiable Credential Verified'
        VC_VERIFICATION_FAILED = 'vc_verification_failed', 'VC Verification Failed'
        VC_REVOKED = 'vc_revoked', 'Verifiable Credential Revoked'

        # Session actions
        SESSION_CREATED = 'session_created', 'Session Created'
        SESSION_EXPIRED = 'session_expired', 'Session Expired'
        SESSION_INVALIDATED = 'session_invalidated', 'Session Invalidated'

        # Admin actions
        USER_UPDATED = 'user_updated', 'User Updated'
        USER_DEACTIVATED = 'user_deactivated', 'User Deactivated'
        USER_REACTIVATED = 'user_reactivated', 'User Reactivated'

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text='User associated with this action'
    )
    user_did = models.CharField(
        'User DID',
        max_length=255,
        blank=True,
        help_text='DID of the user (if applicable)'
    )
    action = models.CharField(
        'Action Type',
        max_length=50,
        choices=ActionType.choices,
        help_text='Type of action performed'
    )
    action_details = models.TextField(
        'Action Details',
        blank=True,
        help_text='Human-readable description of the action'
    )
    metadata = models.JSONField(
        'Metadata',
        default=dict,
        blank=True,
        help_text='Additional action-specific data (IP, user agent, etc.)'
    )
    ip_address = models.GenericIPAddressField(
        'IP Address',
        null=True,
        blank=True,
        help_text='Client IP address'
    )
    user_agent = models.CharField(
        'User Agent',
        max_length=500,
        blank=True,
        help_text='Client user agent string'
    )
    checksum = models.CharField(
        'Checksum',
        max_length=64,
        blank=True,
        help_text='SHA-256 checksum for integrity verification'
    )
    created_at = models.DateTimeField(
        'Timestamp',
        auto_now_add=True,
        help_text='When the action occurred'
    )

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user_did', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f"{self.action} - {self.user_did or self.user} - {self.created_at}"

    def save(self, *args, **kwargs):
        """Calculate checksum for integrity verification."""
        if not self.checksum:
            self.checksum = self._calculate_checksum()
        super().save(*args, **kwargs)

    def _calculate_checksum(self):
        """Calculate SHA-256 checksum of log entry."""
        data = f"{self.user_id or ''}:{self.user_did or ''}:{self.action}:{self.action_details or ''}:{self.created_at.isoformat() if self.created_at else ''}"
        return hashlib.sha256(data.encode()).hexdigest()

    @classmethod
    def log_action(cls, user=None, user_did=None, action=None, action_details='', metadata=None, request=None):
        """
        Convenience method to create an audit log entry.
        """
        ip_address = None
        user_agent = None

        if request:
            ip_address = cls._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        return cls.objects.create(
            user=user,
            user_did=user_did or (user.did if user else None),
            action=action,
            action_details=action_details,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class SessionAudit(models.Model):
    """
    Extended session tracking for security monitoring.
    """

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='session_audits'
    )
    session_key = models.CharField(
        'Session Key',
        max_length=40,
        help_text='Django session key'
    )
    did = models.CharField(
        'User DID',
        max_length=255,
        blank=True,
        help_text='DID used for authentication'
    )
    ip_address = models.GenericIPAddressField('IP Address')
    user_agent = models.CharField(max_length=500, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        return f"Session {self.session_key[:8]}... for {self.user}"