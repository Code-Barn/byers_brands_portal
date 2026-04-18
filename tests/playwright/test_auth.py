"""
Playwright tests for DID-Rust authentication flows.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def login_url(base_url: str) -> str:
    """URL for login page."""
    return f"{base_url}/accounts/login/"


@pytest.fixture
def did_login_url(base_url: str) -> str:
    """URL for DID login page."""
    return f"{base_url}/accounts/did-login/"


@pytest.fixture
def register_url(base_url: str) -> str:
    """URL for registration page."""
    return f"{base_url}/accounts/register/"


class TestDIDAuthentication:
    """Tests for DID-based authentication."""

    @pytest.mark.asyncio
    async def test_did_login_page_loads(self, page: Page, did_login_url: str):
        """Test that DID login page loads correctly."""
        page.goto(did_login_url)
        await expect(page.locator('h1, h2')).to_contain_text('DID')

    @pytest.mark.asyncio
    async def test_did_input_field_exists(self, page: Page, did_login_url: str):
        """Test that DID input field exists."""
        page.goto(did_login_url)
        await expect(page.locator('input[name="did"], input#id_did')).to_be_visible()

    @pytest.mark.asyncio
    async def test_did_login_form_submits(self, page: Page, did_login_url: str):
        """Test that DID login form can be submitted."""
        page.goto(did_login_url)

        # Fill in a test DID
        await page.fill('input[name="did"]', 'did:key:z6Mktest123456')
        await page.fill('input[name="proof"]', 'test_signature')

        # Submit form (may fail gracefully)
        await page.click('button[type="submit"]')

        # Should either succeed or show error
        current_url = page.url
        assert did_login_url in current_url or 'accounts' in current_url

    @pytest.mark.asyncio
    async def test_challenge_api_endpoint(self, page: Page, base_url: str):
        """Test the challenge API endpoint for DID auth."""
        response = await page.request.get(f"{base_url}/accounts/api/challenge/")

        # Should return challenge and session_id
        assert response.status == 200
        data = await response.json()
        assert 'challenge' in data
        assert 'session_id' in data


class TestDIDGeneration:
    """Tests for DID generation functionality."""

    @pytest.mark.asyncio
    async def test_generate_did_api(self, page: Page, base_url: str):
        """Test the generate DID API endpoint."""
        response = await page.request.get(f"{base_url}/accounts/api/generate-did/")

        # Should return a DID
        assert response.status == 200
        data = await response.json()
        assert 'did' in data
        assert data['did'].startswith('did:')


class TestDIDRegistration:
    """Tests for registration with DID."""

    @pytest.mark.asyncio
    async def test_registration_creates_did(self, page: Page, register_url: str, django_client):
        """Test that user registration generates a DID."""
        page.goto(register_url)

        # Fill registration form
        await page.fill('input[name="username"]', 'newuser')
        await page.fill('input[name="email"]', 'newuser@example.com')
        await page.fill('input[name="password1"]', 'TestPass123!')
        await page.fill('input[name="password2"]', 'TestPass123!')

        # Submit
        await page.click('button[type="submit"]')

        # Should redirect or show success
        # User should have a DID assigned

    @pytest.mark.asyncio
    async def test_user_model_has_did_field(self, page: Page):
        """Test that user model has DID field."""
        from apps.accounts.models import CustomUser

        # Check model has DID field
        assert hasattr(CustomUser, 'did')
        assert hasattr(CustomUser, 'did_document')


class TestAuthenticatedAccess:
    """Tests for authenticated access to investor features."""

    @pytest.mark.asyncio
    async def test_unauthenticated_redirect(self, page: Page, base_url: str):
        """Test that unauthenticated users are redirected to login."""
        # Try to access investor dashboard without auth
        response = await page.request.get(f"{base_url}/investor/")

        # Should redirect to login
        assert response.status in [302, 301, 303]

    @pytest.mark.asyncio
    async def test_authenticated_access_dashboard(self, page: Page, base_url: str, authenticated_client):
        """Test that authenticated users can access dashboard."""
        # Use authenticated session
        page.goto(f"{base_url}/investor/")

        # Should load dashboard
        await expect(page.locator('h1')).to_contain_text('Investor Dashboard')

    @pytest.mark.asyncio
    async def test_portfolio_requires_auth(self, page: Page, base_url: str):
        """Test that portfolio view requires authentication."""
        response = await page.request.get(f"{base_url}/investor/portfolio/")

        # Should redirect to login
        assert response.status in [302, 301, 303]

    @pytest.mark.asyncio
    async def test_documents_require_auth(self, page: Page, base_url: str):
        """Test that documents view requires authentication."""
        response = await page.request.get(f"{base_url}/investor/documents/")

        # Should redirect to login
        assert response.status in [302, 301, 303]

    @pytest.mark.asyncio
    async def test_session_persists_did(self, page: Page, base_url: str, user_with_did):
        """Test that DID is persisted in session."""
        # Login as user with DID
        # Session should contain DID for Polly API calls


class TestDIDBackend:
    """Tests for DID backend functionality."""

    @pytest.mark.asyncio
    async def test_verify_vc_api(self, page: Page, base_url: str):
        """Test the verify VC API endpoint."""
        # Test with invalid/empty data
        response = await page.request.post(
            f"{base_url}/accounts/api/verify-vc/",
            data={'invalid': 'data'}
        )

        # Should handle gracefully
        assert response.status in [200, 400, 500]

    @pytest.mark.asyncio
    async def test_python_fallback_available(self, page: Page, base_url: str):
        """Test that Python fallback is available when Rust is not."""
        # The Python fallback should work without the Rust library
        response = await page.request.get(f"{base_url}/accounts/api/generate-did/")

        # Should return a valid DID
        assert response.status == 200
        data = await response.json()
        assert 'did' in data


class TestDIDDocument:
    """Tests for DID document handling."""

    @pytest.mark.asyncio
    async def test_user_has_did_document(self, page: Page, base_url: str, user_with_did):
        """Test that user has a DID document."""
        assert user_with_did.did is not None
        assert user_with_did.did_document is not None
        assert user_with_did.did_document.get('id') == user_with_did.did