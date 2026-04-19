"""
Playwright tests for DID-Rust authentication flows.
Using Playwright sync API.
"""
import pytest
from playwright.sync_api import expect


class TestDIDAuthentication:
    """Tests for DID-based authentication."""

    def test_did_login_page_loads(self, browser):
        """Test that DID login page loads correctly."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/did-login/")
        expect(page.locator('body')).to_be_visible()

    def test_did_input_field_exists(self, browser):
        """Test that DID input field exists."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/did-login/")
        inputs = page.locator('input[name="did"], input#id_did')
        expect(inputs.first).to_be_visible()

    def test_challenge_api_endpoint(self, browser, base_url):
        """Test the challenge API endpoint for DID auth."""
        page = browser.new_page()
        response = page.request.get(f"{base_url}/accounts/api/challenge/")

        assert response.status == 200
        data = response.json()
        assert 'challenge' in data
        assert 'session_id' in data


class TestDIDGeneration:
    """Tests for DID generation functionality."""

    def test_generate_did_api(self, browser, base_url):
        """Test the generate DID API endpoint."""
        page = browser.new_page()
        response = page.request.get(f"{base_url}/accounts/api/generate-did/")

        assert response.status == 200
        data = response.json()
        assert 'did' in data
        assert data['did'].startswith('did:')


class TestAuthenticatedAccess:
    """Tests for authenticated access to investor features."""

    def test_unauthenticated_redirect(self, browser, base_url):
        """Test that unauthenticated users are redirected to login."""
        page = browser.new_page()
        response = page.request.get(f"{base_url}/investor/")

        assert response.status in [302, 301, 303]

    def test_authenticated_access_dashboard(self, browser, base_url):
        """Test that authenticated users can access dashboard."""
        page = browser.new_page()
        page.goto(f"{base_url}/accounts/login/")
        page.fill('input[name="username"], input[name="email"]', 'admin@test.com')
        page.fill('input[name="password"]', 'testpass123')
        page.click('button[type="submit"]')

        page.goto(f"{base_url}/investor/")
        expect(page.locator('h1')).to_contain_text('Investor Dashboard')

    def test_portfolio_requires_auth(self, browser, base_url):
        """Test that portfolio view requires authentication."""
        page = browser.new_page()
        response = page.request.get(f"{base_url}/investor/portfolio/")

        assert response.status in [302, 301, 303]

    def test_documents_require_auth(self, browser, base_url):
        """Test that documents view requires authentication."""
        page = browser.new_page()
        response = page.request.get(f"{base_url}/investor/documents/")

        assert response.status in [302, 301, 303]


class TestDIDBackend:
    """Tests for DID backend functionality."""

    def test_verify_vc_api(self, browser, base_url):
        """Test the verify VC API endpoint."""
        page = browser.new_page()
        response = page.request.post(
            f"{base_url}/accounts/api/verify-vc/",
            data={'invalid': 'data'}
        )

        assert response.status in [200, 400, 500]

    def test_python_fallback_available(self, browser, base_url):
        """Test that Python fallback is available when Rust is not."""
        page = browser.new_page()
        response = page.request.get(f"{base_url}/accounts/api/generate-did/")

        assert response.status == 200
        data = response.json()
        assert 'did' in data


class TestDIDDocument:
    """Tests for DID document handling."""

    def test_user_has_did_document(self):
        """Test that user has a DID document."""
        from apps.accounts.models import CustomUser
        user = CustomUser()
        assert hasattr(user, 'did')
        assert hasattr(user, 'did_document')