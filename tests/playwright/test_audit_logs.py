"""
Playwright tests for Audit Logs.
Using Playwright sync API.
"""
import pytest


class TestAuditLogModel:
    """Tests for AuditLog model."""

    def test_audit_log_model_exists(self):
        """Test that AuditLog model exists."""
        from apps.accounts.audit_models import AuditLog
        assert AuditLog is not None

    def test_audit_log_action_types(self):
        """Test AuditLog action types are defined."""
        from apps.accounts.audit_models import AuditLog
        assert hasattr(AuditLog.ActionType, 'LOGIN')
        assert hasattr(AuditLog.ActionType, 'LOGOUT')
        assert hasattr(AuditLog.ActionType, 'MFA_ENABLED')
        assert hasattr(AuditLog.ActionType, 'VC_VERIFIED')

    def test_audit_log_fields(self):
        """Test AuditLog has expected fields."""
        from apps.accounts.audit_models import AuditLog
        fields = ['user', 'user_did', 'action', 'action_details', 'metadata', 'ip_address', 'user_agent', 'checksum', 'created_at']
        for field in fields:
            assert hasattr(AuditLog, field)

    def test_audit_log_checksum(self):
        """Test that audit log calculates checksum."""
        from apps.accounts.audit_models import AuditLog
        log = AuditLog.objects.create(
            action=AuditLog.ActionType.LOGIN,
            action_details='Test'
        )
        assert log.checksum is not None
        assert len(log.checksum) == 64


class TestAuditLogAdmin:
    """Tests for AuditLog admin interface."""

    def test_audit_log_admin_registered(self):
        """Test that AuditLog is registered with admin."""
        from django.contrib import admin
        from apps.accounts.admin import AuditLogAdmin
        site = admin.site
        assert 'AuditLog' in site._registry


class TestSessionAudit:
    """Tests for SessionAudit model."""

    def test_session_audit_model_exists(self):
        """Test that SessionAudit model exists."""
        from apps.accounts.audit_models import SessionAudit
        assert SessionAudit is not None

    def test_session_audit_fields(self):
        """Test SessionAudit has expected fields."""
        from apps.accounts.audit_models import SessionAudit
        fields = ['user', 'session_key', 'did', 'ip_address', 'started_at', 'last_activity', 'is_active']
        for field in fields:
            assert hasattr(SessionAudit, field)


class TestVCVerificationLogging:
    """Tests for VC verification audit logging."""

    def test_log_vc_issuance(self):
        """Test VC issuance logging."""
        from apps.accounts.audit_models import AuditLog
        from apps.accounts.middleware import DIDOperationLogger

        initial_count = AuditLog.objects.count()

        DIDOperationLogger.log_vc_issuance(
            user=None,
            did='did:key:test',
            vc_id=1,
            credential_type='InvestmentCredential'
        )

        assert AuditLog.objects.count() == initial_count + 1

    def test_log_vc_verification(self):
        """Test VC verification logging."""
        from apps.accounts.audit_models import AuditLog
        from apps.accounts.middleware import DIDOperationLogger

        initial_count = AuditLog.objects.count()

        DIDOperationLogger.log_vc_verification(
            user=None,
            did='did:key:test',
            vc_id=1,
            success=True
        )

        assert AuditLog.objects.count() == initial_count + 1

    def test_log_mfa_action(self):
        """Test MFA action logging."""
        from apps.accounts.audit_models import AuditLog
        from apps.accounts.middleware import DIDOperationLogger

        initial_count = AuditLog.objects.count()

        DIDOperationLogger.log_mfa_action(
            user=None,
            action_type=AuditLog.ActionType.MFA_VERIFIED,
            success=True
        )

        assert AuditLog.objects.count() == initial_count + 1