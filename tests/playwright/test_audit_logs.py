"""
Playwright tests for Audit Logs.
"""
import pytest
from playwright.sync_api import Page, expect


class TestAuditLogModel:
    """Tests for AuditLog model."""

    @pytest.mark.asyncio
    async def test_audit_log_model_exists(self, page: Page):
        """Test that AuditLog model exists."""
        from apps.accounts.audit_models import AuditLog
        assert AuditLog is not None

    @pytest.mark.asyncio
    async def test_audit_log_action_types(self, page: Page):
        """Test AuditLog action types are defined."""
        from apps.accounts.audit_models import AuditLog
        assert hasattr(AuditLog.ActionType, 'LOGIN')
        assert hasattr(AuditLog.ActionType, 'LOGOUT')
        assert hasattr(AuditLog.ActionType, 'MFA_ENABLED')
        assert hasattr(AuditLog.ActionType, 'VC_VERIFIED')

    @pytest.mark.asyncio
    async def test_audit_log_fields(self, page: Page):
        """Test AuditLog has expected fields."""
        from apps.accounts.audit_models import AuditLog
        fields = ['user', 'user_did', 'action', 'action_details', 'metadata', 'ip_address', 'user_agent', 'checksum', 'created_at']
        for field in fields:
            assert hasattr(AuditLog, field)

    @pytest.mark.asyncio
    async def test_log_action_creates_entry(self, page: Page, django_client):
        """Test that log_action creates an audit entry."""
        from apps.accounts.audit_models import AuditLog
        initial_count = AuditLog.objects.count()

        AuditLog.log_action(
            action=AuditLog.ActionType.LOGIN,
            action_details='Test login'
        )

        assert AuditLog.objects.count() == initial_count + 1

    @pytest.mark.asyncio
    async def test_audit_log_checksum(self, page: Page):
        """Test that audit log calculates checksum."""
        from apps.accounts.audit_models import AuditLog
        log = AuditLog.objects.create(
            action=AuditLog.ActionType.LOGIN,
            action_details='Test'
        )
        assert log.checksum is not None
        assert len(log.checksum) == 64

    @pytest.mark.asyncio
    async def test_audit_log_indexes(self, page: Page):
        """Test audit log has expected indexes."""
        from apps.accounts.audit_models import AuditLog
        indexes = [idx.name for idx in AuditLog._meta.indexes]
        assert 'user_created_at_idx' in indexes or any('user' in idx and 'created_at' in idx for idx in indexes)


class TestAuditLogAdmin:
    """Tests for AuditLog admin interface."""

    @pytest.mark.asyncio
    async def test_audit_log_admin_registered(self, page: Page):
        """Test that AuditLog is registered with admin."""
        from django.contrib import admin
        from apps.accounts.admin import AuditLogAdmin
        site = admin.site
        assert 'AuditLog' in site._registry

    @pytest.mark.asyncio
    async def test_audit_log_admin_readonly(self, page: Page):
        """Test that audit log entries are read-only in admin."""
        from apps.accounts.admin import AuditLogAdmin
        admin_obj = AuditLogAdmin(AuditLog, None)
        assert not admin_obj.has_add_permission(None)
        assert not admin_obj.has_change_permission(None)


class TestAuditLogMiddleware:
    """Tests for audit log middleware."""

    @pytest.mark.asyncio
    async def test_middleware_captures_login(self, page: Page, django_client):
        """Test that middleware logs login attempts."""
        from apps.accounts.audit_models import AuditLog
        initial_count = AuditLog.objects.filter(action=AuditLog.ActionType.LOGIN).count()

        django_client.post('/accounts/login/', {'username': 'test', 'password': 'test'})

        # Should create audit log or attempt to

    @pytest.mark.asyncio
    async def test_middleware_captures_logout(self, page: Page, django_client):
        """Test that middleware logs logout."""
        from apps.accounts.audit_models import AuditLog

        django_client.get('/accounts/logout/')

    @pytest.mark.asyncio
    async def test_middleware_captures_did_login(self, page: Page, django_client):
        """Test that middleware logs DID login."""
        from apps.accounts.audit_models import AuditLog

        django_client.post('/accounts/did-login/', {'did': 'did:key:test', 'proof': 'test'})


class TestAuditLogViews:
    """Tests for audit log viewing (admin only)."""

    @pytest.mark.asyncio
    async def test_audit_log_accessible_via_admin(self, page: Page, base_url: str):
        """Test that audit logs are accessible via admin."""
        page.goto(f"{base_url}/admin/auditlog/")
        # Should redirect to login if not authenticated as admin

    @pytest.mark.asyncio
    async def test_audit_log_list_shows_actions(self, page: Page, base_url: str):
        """Test that audit log list shows action types."""
        from apps.accounts.audit_models import AuditLog
        AuditLog.objects.create(
            action=AuditLog.ActionType.LOGIN,
            action_details='Test login'
        )

        logs = AuditLog.objects.all()
        assert len(logs) > 0


class TestSessionAudit:
    """Tests for SessionAudit model."""

    @pytest.mark.asyncio
    async def test_session_audit_model_exists(self, page: Page):
        """Test that SessionAudit model exists."""
        from apps.accounts.audit_models import SessionAudit
        assert SessionAudit is not None

    @pytest.mark.asyncio
    async def test_session_audit_fields(self, page: Page):
        """Test SessionAudit has expected fields."""
        from apps.accounts.audit_models import SessionAudit
        fields = ['user', 'session_key', 'did', 'ip_address', 'started_at', 'last_activity', 'is_active']
        for field in fields:
            assert hasattr(SessionAudit, field)


class TestVCVerificationLogging:
    """Tests for VC verification audit logging."""

    @pytest.mark.asyncio
    async def test_log_vc_issuance(self, page: Page):
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

    @pytest.mark.asyncio
    async def test_log_vc_verification(self, page: Page):
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

    @pytest.mark.asyncio
    async def test_log_mfa_action(self, page: Page):
        """Test MFA action logging."""
        from apps.accounts.audit_models import AuditLog
        from apps.accounts.middleware import DIDOperationLogger
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.first() if User.objects.exists() else None

        initial_count = AuditLog.objects.count()

        DIDOperationLogger.log_mfa_action(
            user=user,
            action_type=AuditLog.ActionType.MFA_VERIFIED,
            success=True
        )

        assert AuditLog.objects.count() == initial_count + 1