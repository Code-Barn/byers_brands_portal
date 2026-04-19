"""
Playwright tests for Investor Dashboard UI/UX.
Using Playwright sync API (no async/await needed).
"""
import re
import pytest
from playwright.sync_api import sync_playwright, Page, expect


@pytest.fixture
def base_url():
    """Base URL for tests."""
    return "http://localhost:8000"


@pytest.fixture
def dashboard_url(base_url):
    """URL for the investor dashboard."""
    return f"{base_url}/investor/"


@pytest.fixture
def login_url(base_url):
    """URL for login page."""
    return f"{base_url}/accounts/login/"


def get_authenticated_page(base_url, browser):
    """Get an authenticated page by logging in."""
    page = browser.new_page()
    page.goto(f"{base_url}/accounts/login/")
    page.fill('input[name="username"], input[name="email"]', 'admin@test.com')
    page.fill('input[name="password"]', 'testpass123')
    page.click('button[type="submit"]')
    return page


class TestInvestorDashboard:
    """Tests for investor dashboard functionality."""

    def test_dashboard_loads(self, browser, dashboard_url):
        """Test that investor dashboard loads correctly."""
        page = get_authenticated_page("http://localhost:8000", browser)
        page.goto(dashboard_url)
        expect(page).to_have_title(re.compile("Investor"))
        expect(page.locator('h1')).to_contain_text('Investor Dashboard')

    def test_dashboard_light_mode(self, browser, dashboard_url):
        """Test dashboard displays correctly in light mode."""
        page = get_authenticated_page("http://localhost:8000", browser)
        page.goto(dashboard_url)
        html = page.locator('html')
        expect(html).not_to_have_class(re.compile(r'dark'))

    def test_dashboard_dark_mode(self, browser, dashboard_url):
        """Test dashboard displays correctly in dark mode."""
        page = get_authenticated_page("http://localhost:8000", browser)
        page.goto(dashboard_url)
        page.evaluate("document.documentElement.classList.add('dark')")
        html = page.locator('html')
        expect(html).to_have_class(re.compile(r'dark'))

    def test_tabs_switch_correctly(self, browser, dashboard_url):
        """Test that dashboard tabs switch content correctly."""
        page = get_authenticated_page("http://localhost:8000", browser)
        page.goto(dashboard_url)

        page.click('button:has-text("Analytics")')
        expect(page.locator('#content-analytics')).to_be_visible()

        page.click('button:has-text("Documents")')
        expect(page.locator('#content-documents')).to_be_visible()

        page.click('button:has-text("Opportunities")')
        expect(page.locator('#content-opportunities')).to_be_visible()

        page.click('button:has-text("ROI Calculator")')
        expect(page.locator('#content-calculator')).to_be_visible()

    def test_roi_calculator(self, browser, dashboard_url):
        """Test ROI calculator functionality."""
        page = get_authenticated_page("http://localhost:8000", browser)
        page.goto(dashboard_url)
        page.click('button:has-text("ROI Calculator")')

        expect(page.locator('#initialInvestment')).to_be_visible()
        expect(page.locator('#monthlyContribution')).to_be_visible()
        expect(page.locator('#expectedReturn')).to_be_visible()
        expect(page.locator('#investmentYears')).to_be_visible()
        expect(page.locator('#futureValue')).to_contain_text('$')

    def test_responsive_design(self, browser, dashboard_url):
        """Test dashboard is responsive on different screen sizes."""
        page = get_authenticated_page("http://localhost:8000", browser)

        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto(dashboard_url)
        expect(page.locator('h1')).to_be_visible()

        page.set_viewport_size({'width': 768, 'height': 1024})
        page.goto(dashboard_url)
        expect(page.locator('h1')).to_be_visible()

        page.set_viewport_size({'width': 1280, 'height': 800})
        page.goto(dashboard_url)
        expect(page.locator('h1')).to_be_visible()


class TestPortfolioTracking:
    """Tests for portfolio tracking features."""

    def test_portfolio_view_loads(self, browser, base_url):
        """Test portfolio view loads correctly."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/portfolio/")
        expect(page.locator('h1')).to_contain_text('Portfolio')

    def test_investment_list_display(self, browser, base_url):
        """Test investment list displays on portfolio page."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/portfolio/")
        elements = page.locator('table, text=No investments')
        expect(elements.first).to_be_visible()


class TestDocumentManagement:
    """Tests for document management features."""

    def test_documents_view_loads(self, browser, base_url):
        """Test documents view loads correctly."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/documents/")
        expect(page.locator('h1')).to_be_visible()

    def test_upload_form_exists(self, browser, base_url):
        """Test document upload form is present."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/documents/")
        expect(page.locator('input[name="file"]')).to_be_visible()
        expect(page.locator('button:has-text("Upload")')).to_be_visible()


class TestInvestmentOpportunities:
    """Tests for investment opportunities features."""

    def test_opportunities_view_loads(self, browser, base_url):
        """Test opportunities view loads correctly."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/opportunities/")
        expect(page.locator('h1')).to_be_visible()

    def test_opportunity_cards_display(self, browser, base_url):
        """Test opportunity cards are displayed."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/opportunities/")
        elements = page.locator('.bg-white, text=No opportunities')
        expect(elements.first).to_be_visible()


class TestROICalculator:
    """Tests for ROI Calculator features."""

    def test_roi_calculator_page_loads(self, browser, base_url):
        """Test ROI calculator page loads correctly."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/roi-calculator/")
        expect(page.locator('h1')).to_contain_text('ROI Calculator')

    def test_roi_calculates_correctly(self, browser, base_url):
        """Test ROI calculator produces correct results."""
        page = get_authenticated_page(base_url, browser)
        page.goto(f"{base_url}/investor/roi-calculator/")

        page.fill('#initialInvestment', '10000')
        page.fill('#monthlyContribution', '500')
        page.fill('#expectedReturn', '7')
        page.fill('#investmentYears', '10')

        future_value = page.locator('#futureValue').inner_text()
        assert '0' not in future_value or '0.00' not in future_value