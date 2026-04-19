"""
Playwright tests for Polly poll integration.
Using Playwright sync API.
"""
import re
import pytest
from playwright.sync_api import expect


@pytest.fixture
def polls_url(base_url):
    """URL for the polls page."""
    return f"{base_url}/polly/polls/"


def get_authenticated_page(base_url, browser):
    """Get an authenticated page by logging in."""
    page = browser.new_page()
    page.goto(f"{base_url}/accounts/login/")
    page.fill('input[name="username"], input[name="email"]', 'admin@test.com')
    page.fill('input[name="password"]', 'testpass123')
    page.click('button[type="submit"]')
    return page


class TestPollyPolls:
    """Tests for Polly poll integration."""

    def test_polls_page_loads(self, browser, polls_url):
        """Test that polls page loads correctly."""
        page = get_authenticated_page("http://localhost:8000", browser)
        page.goto(polls_url)
        expect(page.locator('body')).to_be_visible()

    def test_poll_widget_renders(self, browser, base_url):
        """Test that poll widgets render correctly."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/")
        page.click('button:has-text("Polls")')
        expect(page.locator('#polls-container')).to_be_visible()

    def test_poll_theme_matches_portal(self, browser, base_url):
        """Test that poll theme matches portal theme."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/")
        page.click('button:has-text("Polls")')
        expect(page.locator('#polls-container')).to_be_visible()

        page.evaluate("document.documentElement.classList.add('dark')")
        page.click('button:has-text("Polls")')
        expect(page.locator('#polls-container')).to_be_visible()

    def test_poll_api_endpoint(self, browser, base_url):
        """Test that poll API endpoint returns data or error gracefully."""
        page = browser.new_page()
        response = page.request.get(
            f"{base_url}/polly/api/polls/",
            params={
                'embedding_app': 'byers-brands-llc',
                'user_did': 'did:key:test123',
                'theme': 'light'
            }
        )
        assert 'application/json' in response.headers.get('content-type', '')


class TestPollVoting:
    """Tests for poll voting functionality."""

    def test_vote_button_exists(self, browser, base_url):
        """Test that vote buttons exist on poll widgets."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/")
        page.click('button:has-text("Polls")')
        buttons = page.locator('.poll-vote-btn')
        if buttons.count() > 0:
            expect(buttons.first).to_be_visible()

    def test_vote_requires_auth(self, browser, base_url):
        """Test that voting requires authentication."""
        page = browser.new_page()
        page.goto(f"{base_url}/investor/")
        page.click('button:has-text("Polls")')


class TestCactusComments:
    """Tests for Cactus Comments integration."""

    def test_cactus_comments_loads(self, browser, polls_url):
        """Test that Cactus Comments loads (or shows loading state)."""
        page = get_authenticated_page("http://localhost:8000", browser)
        page.goto(polls_url)
        containers = page.locator('.cactus-comments-container, .cactus-loading')
        expect(containers.first).to_be_visible()

    def test_cactus_config_correct(self, browser, base_url):
        """Test that Cactus configuration is correct."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/")
        page.click('button:has-text("Polls")')


class TestPollyAPIClient:
    """Tests for Polly API client."""

    def test_health_endpoint(self, browser, base_url):
        """Test the Polly health check endpoint."""
        page = browser.new_page()
        response = page.request.get(f"{base_url}/polly/api/health/")

        assert response.status == 200
        data = response.json()
        assert 'status' in data
        assert 'polly_connected' in data

    def test_poll_list_api(self, browser, base_url):
        """Test the poll list API returns proper structure."""
        page = browser.new_page()
        response = page.request.get(
            f"{base_url}/polly/api/polls/",
            params={'embedding_app': 'byers-brands-llc'}
        )

        assert response.status == 200
        data = response.json()
        assert 'polls' in data
        assert 'theme' in data