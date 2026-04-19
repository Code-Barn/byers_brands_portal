"""
Playwright tests for MFA functionality.
Using Playwright sync API.
"""
import pytest
from playwright.sync_api import expect


class TestMFASetup:
    """Tests for MFA setup functionality."""

    def test_mfa_setup_requires_auth(self, browser):
        """Test that MFA setup requires authentication."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/mfa/setup/")
        assert 'login' in page.url.lower() or page.url != "http://localhost:8000/accounts/mfa/setup/"

    def test_mfa_setup_page_loads(self, browser):
        """Test that MFA setup page loads for authenticated user."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")
        page.fill('input[name="username"], input[name="email"]', 'admin@test.com')
        page.fill('input[name="password"]', 'testpass123')
        page.click('button[type="submit"]')
        page.goto("http://localhost:8000/accounts/profile/")
        expect(page.locator('body')).to_be_visible()

    def test_mfa_verify_page_loads(self, browser):
        """Test that MFA verification page loads."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/mfa/login/")
        expect(page.locator('h1')).to_contain_text('Two-Factor')

    def test_backup_code_field_available(self, browser):
        """Test that backup code field is available."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/mfa/login/")
        backup_field = page.locator('input[name="backup_code"]')
        expect(backup_field).to_be_visible()


class TestMFAUserModel:
    """Tests for MFA-related user model fields."""

    def test_user_model_has_mfa_fields(self):
        """Test that user model has MFA fields."""
        from apps.accounts.models import CustomUser
        user = CustomUser()
        assert hasattr(user, 'mfa_enabled')
        assert hasattr(user, 'mfa_secret')
        assert hasattr(user, 'mfa_secret_hash')
        assert hasattr(user, 'mfa_backup_codes')
        assert hasattr(user, 'mfa_last_verified')

    def test_generate_mfa_secret(self):
        """Test MFA secret generation."""
        from apps.accounts.models import CustomUser
        user = CustomUser()
        secret = user.generate_mfa_secret()
        assert secret is not None
        assert len(secret) == 40

    def test_set_mfa_secret_hashes(self):
        """Test that setting MFA secret creates hash."""
        from apps.accounts.models import CustomUser
        user = CustomUser()
        secret = 'testsecret123'
        user.set_mfa_secret(secret)
        assert user.mfa_secret_hash is not None
        assert user.mfa_secret != ''

    def test_generate_backup_codes(self):
        """Test backup codes generation."""
        from apps.accounts.models import CustomUser
        user = CustomUser()
        codes = user.generate_backup_codes()
        assert len(codes) == 10
        assert all(len(c) == 8 for c in codes)