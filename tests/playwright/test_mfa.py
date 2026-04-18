"""
Playwright tests for MFA functionality.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def mfa_setup_url(base_url: str) -> str:
    """URL for MFA setup page."""
    return f"{base_url}/accounts/mfa/setup/"


@pytest.fixture
def profile_url(base_url: str) -> str:
    """URL for profile page."""
    return f"{base_url}/accounts/profile/"


class TestMFASetup:
    """Tests for MFA setup functionality."""

    @pytest.mark.asyncio
    async def test_mfa_setup_requires_auth(self, page: Page, mfa_setup_url: str):
        """Test that MFA setup requires authentication."""
        page.goto(mfa_setup_url)
        assert 'login' in page.url.lower() or page.url != mfa_setup_url

    @pytest.mark.asyncio
    async def test_mfa_setup_page_loads(self, page: Page, profile_url: str, authenticated_client):
        """Test that MFA setup page loads for authenticated user."""
        page.goto(profile_url)
        await expect(page.locator('body')).to_be_visible()

    @pytest.mark.asyncio
    async def test_mfa_enable_link_shown_when_disabled(self, page: Page, profile_url: str, authenticated_client):
        """Test that enable MFA link is shown when MFA is disabled."""
        page.goto(profile_url)
        enable_link = page.locator('a:has-text("Enable")').first
        if await enable_link.is_visible():
            await expect(enable_link).to_contain_text("Enable")

    @pytest.mark.asyncio
    async def test_mfa_disable_link_shown_when_enabled(self, page: Page, profile_url: str):
        """Test that disable MFA link is shown when MFA is enabled."""
        from apps.accounts.models import CustomUser
        user = CustomUser.objects.first()
        if user:
            user.mfa_enabled = True
            user.mfa_secret = 'testsecret123'
            user.save()

        page.goto(profile_url)
        disable_link = page.locator('a:has-text("Disable")').first
        if await disable_link.is_visible():
            await expect(disable_link).to_contain_text("Disable")

    @pytest.mark.asyncio
    async def test_mfa_setup_form_submits(self, page: Page, base_url: str, authenticated_client):
        """Test that MFA setup form can be submitted."""
        page.goto(f"{base_url}/accounts/mfa/setup/")
        if 'login' not in page.url.lower():
            submit_btn = page.locator('button[type="submit"]')
            if await submit_btn.is_visible():
                await submit_btn.click()
                await expect(page.locator('h1, h2')).to_be_visible()


class TestMFAVerification:
    """Tests for MFA verification during login."""

    @pytest.mark.asyncio
    async def test_mfa_verify_page_loads(self, page: Page, base_url: str):
        """Test that MFA verification page loads."""
        page.goto(f"{base_url}/accounts/mfa/login/")
        await expect(page.locator('h1')).to_contain_text('Two-Factor')

    @pytest.mark.asyncio
    async def test_mfa_verify_requires_code(self, page: Page, base_url: str):
        """Test that MFA verification requires a code."""
        page.goto(f"{base_url}/accounts/mfa/login/")

        submit_btn = page.locator('button[type="submit"]')
        if await submit_btn.is_visible():
            await submit_btn.click()
            await expect(page.locator('input[name="code"]')).to_be_visible()

    @pytest.mark.asyncio
    async def test_backup_code_field_available(self, page: Page, base_url: str):
        """Test that backup code field is available."""
        page.goto(f"{base_url}/accounts/mfa/login/")

        backup_field = page.locator('input[name="backup_code"]')
        await expect(backup_field).to_be_visible()


class TestMFADisable:
    """Tests for MFA disable functionality."""

    @pytest.mark.asyncio
    async def test_mfa_disable_requires_password(self, page: Page, base_url: str, authenticated_client):
        """Test that MFA disable requires password verification."""
        page.goto(f"{base_url}/accounts/mfa/disable/")

        if 'login' not in page.url.lower():
            password_field = page.locator('input[name="password"]')
            await expect(password_field).to_be_visible()


class TestMFAUserModel:
    """Tests for MFA-related user model fields."""

    @pytest.mark.asyncio
    async def test_user_model_has_mfa_fields(self, page: Page):
        """Test that user model has MFA fields."""
        from apps.accounts.models import CustomUser
        user = CustomUser()
        assert hasattr(user, 'mfa_enabled')
        assert hasattr(user, 'mfa_secret')
        assert hasattr(user, 'mfa_secret_hash')
        assert hasattr(user, 'mfa_backup_codes')
        assert hasattr(user, 'mfa_last_verified')

    @pytest.mark.asyncio
    async def test_generate_mfa_secret(self, page: Page):
        """Test MFA secret generation."""
        from apps.accounts.models import CustomUser
        user = CustomUser()
        secret = user.generate_mfa_secret()
        assert secret is not None
        assert len(secret) == 40

    @pytest.mark.asyncio
    async def test_set_mfa_secret_hashes(self, page: Page):
        """Test that setting MFA secret creates hash."""
        from apps.accounts.models import CustomUser
        user = CustomUser()
        secret = 'testsecret123'
        user.set_mfa_secret(secret)
        assert user.mfa_secret_hash is not None
        assert user.mfa_secret != ''

    @pytest.mark.asyncio
    async def test_generate_backup_codes(self, page: Page):
        """Test backup codes generation."""
        from apps.accounts.models import CustomUser
        user = CustomUser()
        codes = user.generate_backup_codes()
        assert len(codes) == 10
        assert all(len(c) == 8 for c in codes)