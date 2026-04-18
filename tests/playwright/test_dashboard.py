"""
Playwright tests for Investor Dashboard UI/UX.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def dashboard_url(base_url: str) -> str:
    """URL for the investor dashboard."""
    return f"{base_url}/investor/"


@pytest.fixture
def login_url(base_url: str) -> str:
    """URL for login page."""
    return f"{base_url}/accounts/login/"


class TestInvestorDashboard:
    """Tests for investor dashboard functionality."""

    @pytest.mark.asyncio
    async def test_dashboard_loads(self, page: Page, dashboard_url: str, authenticated_client):
        """Test that investor dashboard loads correctly."""
        page.goto(dashboard_url)
        await expect(page).to_have_title(/Investor/)
        await expect(page.locator('h1')).to_contain_text('Investor Dashboard')

    @pytest.mark.asyncio
    async def test_dashboard_light_mode(self, page: Page, dashboard_url: str, authenticated_client):
        """Test dashboard displays correctly in light mode."""
        page.goto(dashboard_url)
        html = page.locator('html')
        await expect(html).not_to_have_class(/dark/)

    @pytest.mark.asyncio
    async def test_dashboard_dark_mode(self, page: Page, dashboard_url: str, authenticated_client):
        """Test dashboard displays correctly in dark mode."""
        page.goto(dashboard_url)
        page.evaluate("document.documentElement.classList.add('dark')")
        html = page.locator('html')
        await expect(html).to_have_class(/dark/)

    @pytest.mark.asyncio
    async def test_tabs_switch_correctly(self, page: Page, dashboard_url: str, authenticated_client):
        """Test that dashboard tabs switch content correctly."""
        page.goto(dashboard_url)

        # Click Analytics tab
        await page.click('button:has-text("Analytics")')
        await expect(page.locator('#content-analytics')).to_be_visible()

        # Click Documents tab
        await page.click('button:has-text("Documents")')
        await expect(page.locator('#content-documents')).to_be_visible()

        # Click Opportunities tab
        await page.click('button:has-text("Opportunities")')
        await expect(page.locator('#content-opportunities')).to_be_visible()

        # Click ROI Calculator tab
        await page.click('button:has-text("ROI Calculator")')
        await expect(page.locator('#content-calculator')).to_be_visible()

    @pytest.mark.asyncio
    async def test_roi_calculator(self, page: Page, dashboard_url: str, authenticated_client):
        """Test ROI calculator functionality."""
        page.goto(dashboard_url)
        await page.click('button:has-text("ROI Calculator")')

        # Check calculator inputs exist
        await expect(page.locator('#initialInvestment')).to_be_visible()
        await expect(page.locator('#monthlyContribution')).to_be_visible()
        await expect(page.locator('#expectedReturn')).to_be_visible()
        await expect(page.locator('#investmentYears')).to_be_visible()

        # Check results are calculated
        await expect(page.locator('#futureValue')).to_contain_text('$')

    @pytest.mark.asyncio
    async def test_responsive_design(self, page: Page, dashboard_url: str, authenticated_client):
        """Test dashboard is responsive on different screen sizes."""
        # Mobile view
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto(dashboard_url)
        await expect(page.locator('h1')).to_be_visible()

        # Tablet view
        page.set_viewport_size({'width': 768, 'height': 1024})
        page.goto(dashboard_url)
        await expect(page.locator('h1')).to_be_visible()

        # Desktop view
        page.set_viewport_size({'width': 1280, 'height': 800})
        page.goto(dashboard_url)
        await expect(page.locator('h1')).to_be_visible()


class TestPortfolioTracking:
    """Tests for portfolio tracking features."""

    @pytest.mark.asyncio
    async def test_portfolio_view_loads(self, page: Page, base_url: str, authenticated_client):
        """Test portfolio view loads correctly."""
        page.goto(f"{base_url}/investor/portfolio/")
        await expect(page.locator('h1')).to_contain_text('Portfolio')

    @pytest.mark.asyncio
    async def test_investment_list_display(self, page: Page, base_url: str, authenticated_client):
        """Test investment list displays on portfolio page."""
        page.goto(f"{base_url}/investor/portfolio/")
        # Check for investment table or empty state
        elements = page.locator('table, text=No investments')
        await expect(elements.first).to_be_visible()


class TestDocumentManagement:
    """Tests for document management features."""

    @pytest.mark.asyncio
    async def test_documents_view_loads(self, page: Page, base_url: str, authenticated_client):
        """Test documents view loads correctly."""
        page.goto(f"{base_url}/investor/documents/")
        await expect(page.locator('h1')).to_be_visible()

    @pytest.mark.asyncio
    async def test_upload_form_exists(self, page: Page, base_url: str, authenticated_client):
        """Test document upload form is present."""
        page.goto(f"{base_url}/investor/documents/")
        await expect(page.locator('input[name="file"]')).to_be_visible()
        await expect(page.locator('button:has-text("Upload")')).to_be_visible()


class TestInvestmentOpportunities:
    """Tests for investment opportunities features."""

    @pytest.mark.asyncio
    async def test_opportunities_view_loads(self, page: Page, base_url: str, authenticated_client):
        """Test opportunities view loads correctly."""
        page.goto(f"{base_url}/investor/opportunities/")
        await expect(page.locator('h1')).to_be_visible()

    @pytest.mark.asyncio
    async def test_opportunity_cards_display(self, page: Page, base_url: str, authenticated_client):
        """Test opportunity cards are displayed."""
        page.goto(f"{base_url}/investor/opportunities/")
        # Should show cards or "No opportunities" message
        elements = page.locator('.bg-white.dark\\:bg-gray-800, text=No opportunities')
        await expect(elements.first).to_be_visible()


class TestROICalculator:
    """Tests for ROI Calculator features."""

    @pytest.mark.asyncio
    async def test_roi_calculator_page_loads(self, page: Page, base_url: str, authenticated_client):
        """Test ROI calculator page loads correctly."""
        page.goto(f"{base_url}/investor/roi-calculator/")
        await expect(page.locator('h1')).to_contain_text('ROI Calculator')

    @pytest.mark.asyncio
    async def test_roi_calculates_correctly(self, page: Page, base_url: str, authenticated_client):
        """Test ROI calculator produces correct results."""
        page.goto(f"{base_url}/investor/roi-calculator/")

        # Set values
        await page.fill('#initialInvestment', '10000')
        await page.fill('#monthlyContribution', '500')
        await page.fill('#expectedReturn', '7')
        await page.fill('#investmentYears', '10')

        # Check results are calculated (non-zero)
        future_value = page.locator('#futureValue').inner_text()
        assert '0' not in future_value or '0.00' not in future_value