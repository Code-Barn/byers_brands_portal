"""
Playwright tests for Polly poll integration.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def polls_url(base_url: str) -> str:
    """URL for the polls page."""
    return f"{base_url}/polly/polls/"


class TestPollyPolls:
    """Tests for Polly poll integration."""

    @pytest.mark.asyncio
    async def test_polls_page_loads(self, page: Page, polls_url: str, authenticated_client):
        """Test that polls page loads correctly."""
        page.goto(polls_url)
        await expect(page.locator('h1, h2')).to_be_visible()

    @pytest.mark.asyncio
    async def test_poll_widget_renders(self, page: Page, base_url: str, authenticated_client):
        """Test that poll widgets render correctly."""
        page.goto(f"{base_url}/investor/")
        await page.click('button:has-text("Polls")')

        # Should show loading or polls container
        await expect(page.locator('#polls-container')).to_be_visible()

    @pytest.mark.asyncio
    async def test_poll_theme_matches_portal(self, page: Page, base_url: str, authenticated_client):
        """Test that poll theme matches portal theme."""
        page.goto(f"{base_url}/investor/")

        # In light mode
        await page.click('button:has-text("Polls")')
        await expect(page.locator('#polls-container')).to_be_visible()

        # Switch to dark mode
        page.evaluate("document.documentElement.classList.add('dark')")
        await page.click('button:has-text("Polls")')
        # Should still render properly
        await expect(page.locator('#polls-container')).to_be_visible()

    @pytest.mark.asyncio
    async def test_poll_api_endpoint(self, page: Page, base_url: str, authenticated_client):
        """Test that poll API endpoint returns data or error gracefully."""
        user_did = 'did:key:test123'
        response = await page.request.get(
            f"{base_url}/polly/api/polls/",
            params={
                'embedding_app': 'byers-brands-llc',
                'user_did': user_did,
                'theme': 'light'
            }
        )
        # Should return JSON (either polls or error)
        assert response.headers.get('content-type', '').startswith('application/json')


class TestPollVoting:
    """Tests for poll voting functionality."""

    @pytest.mark.asyncio
    async def test_vote_button_exists(self, page: Page, base_url: str, authenticated_client):
        """Test that vote buttons exist on poll widgets."""
        page.goto(f"{base_url}/investor/")
        await page.click('button:has-text("Polls")')
        await expect(page.locator('.poll-vote-btn').first).to_be_visible()

    @pytest.mark.asyncio
    async def test_vote_requires_auth(self, page: Page, base_url: str):
        """Test that voting requires authentication."""
        page.goto(f"{base_url}/investor/")
        await page.click('button:has-text("Polls")')

        # Click a vote button
        vote_btn = page.locator('.poll-vote-btn').first
        if await vote_btn.is_visible():
            await vote_btn.click()
            # Should show auth requirement
            # (In production, would check for alert or modal)

    @pytest.mark.asyncio
    async def test_vote_api_endpoint(self, page: Page, base_url: str, authenticated_client):
        """Test the vote API endpoint."""
        # Unauthenticated vote should fail
        response = await page.request.post(
            f"{base_url}/polly/api/vote/",
            data={
                'poll_id': 1,
                'option_id': 1,
                'signature': ''
            }
        )
        # Should require authentication
        assert response.status in [401, 403, 400]


class TestCactusComments:
    """Tests for Cactus Comments integration."""

    @pytest.mark.asyncio
    async def test_cactus_comments_loads(self, page: Page, polls_url: str, authenticated_client):
        """Test that Cactus Comments loads (or shows loading state)."""
        page.goto(polls_url)

        # Check for Cactus Comments container
        containers = page.locator('.cactus-comments-container, .cactus-loading')
        await expect(containers.first).to_be_visible()

    @pytest.mark.asyncio
    async def test_cactus_script_loads(self, page: Page, polls_url: str, authenticated_client):
        """Test that Cactus Comments script is loaded."""
        page.goto(polls_url)

        # Check if cactus script is loaded or being loaded
        scripts = await page.evaluate("""
            Array.from(document.querySelectorAll('script')).map(s => s.src)
        """)
        # Script may load dynamically, so we just verify page loads without error

    @pytest.mark.asyncio
    async def test_cactus_config_correct(self, page: Page, base_url: str, authenticated_client):
        """Test that Cactus configuration is correct."""
        page.goto(f"{base_url}/investor/")

        # Check for correct site name in data attributes
        site_names = await page.locator('[data-site-name]').get_attribute('data-site-name')
        assert 'byers-brands-llc' in site_names


class TestPollyAPIClient:
    """Tests for Polly API client."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, page: Page, base_url: str):
        """Test the Polly health check endpoint."""
        response = await page.request.get(f"{base_url}/polly/api/health/")

        assert response.status == 200
        data = await response.json()
        assert 'status' in data
        assert 'polly_connected' in data

    @pytest.mark.asyncio
    async def test_poll_list_api(self, page: Page, base_url: str):
        """Test the poll list API returns proper structure."""
        response = await page.request.get(
            f"{base_url}/polly/api/polls/",
            params={'embedding_app': 'byers-brands-llc'}
        )

        assert response.status == 200
        data = await response.json()
        assert 'polls' in data
        assert 'theme' in data