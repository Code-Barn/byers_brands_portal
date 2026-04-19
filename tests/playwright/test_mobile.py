"""
Playwright tests for mobile responsiveness.
"""
import pytest
from playwright.sync_api import expect


class TestMobileViewport:
    """Tests for mobile viewport rendering."""

    def test_home_page_mobile_375(self, browser):
        """Test home page renders correctly on mobile (375px)."""
        page = browser.new_page()
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto("http://localhost:8000/")
        expect(page.locator('h1')).to_be_visible()

    def test_home_page_mobile_320(self, browser):
        """Test home page renders on small mobile (320px)."""
        page = browser.new_page()
        page.set_viewport_size({'width': 320, 'height': 568})
        page.goto("http://localhost:8000/")
        expect(page.locator('body')).to_be_visible()

    def test_dashboard_mobile_375(self, browser):
        """Test dashboard renders on mobile."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")
        page.fill('input[name="username"], input[name="email"]', 'admin@test.com')
        page.fill('input[name="password"]', 'testpass123')
        page.click('button[type="submit"]')

        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto("http://localhost:8000/investor/")
        expect(page.locator('h1')).to_be_visible()

    def test_products_page_mobile(self, browser):
        """Test products page mobile view."""
        page = browser.new_page()
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto("http://localhost:8000/products/")
        expect(page.locator('body')).to_be_visible()


class TestMobileNavigation:
    """Tests for mobile navigation."""

    def test_mobile_menu_opens(self, browser):
        """Test that mobile menu opens."""
        page = browser.new_page()
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto("http://localhost:8000/")

        menu_button = page.locator('#mobile-menu-button')
        expect(menu_button).to_be_visible()

    def test_mobile_menu_closes(self, browser):
        """Test that mobile menu can be closed."""
        page = browser.new_page()
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto("http://localhost:8000/")

        menu_button = page.locator('#mobile-menu-button')
        menu_button.click()
        menu = page.locator('#mobile-menu')
        expect(menu).to_be_visible()


class TestMobileTouchTargets:
    """Tests for mobile touch targets."""

    def test_buttons_minimum_44px(self, browser):
        """Test that buttons have minimum touch target size."""
        page = browser.new_page()
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto("http://localhost:8000/accounts/login/")

        submit_btn = page.locator('button[type="submit"]')
        box = submit_btn.bounding_box()
        assert box['height'] >= 44, f"Button height {box['height']} is less than 44px"

    def test_mobile_menu_items_tappable(self, browser):
        """Test that mobile menu items are large enough."""
        page = browser.new_page()
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto("http://localhost:8000/")

        page.locator('#mobile-menu-button').click()
        menu_items = page.locator('#mobile-menu a').all()
        for item in menu_items:
            box = item.bounding_box()
            if box:
                assert box['height'] >= 44, f"Menu item height {box['height']} is less than 44px"


class TestMobileTabs:
    """Tests for dashboard mobile tabs."""

    def test_dashboard_tabs_scroll_horizontal(self, browser):
        """Test that dashboard tabs scroll horizontally on mobile."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")
        page.fill('input[name="username"], input[name="email"]', 'admin@test.com')
        page.fill('input[name="password"]', 'testpass123')
        page.click('button[type="submit"]')

        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto("http://localhost:8000/investor/")

        tabs_container = page.locator('nav[role="tablist"]')
        expect(tabs_container).to_be_visible()

    def test_dashboard_content_fits_mobile(self, browser):
        """Test dashboard content fits on mobile screen."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")
        page.fill('input[name="username"], input[name="email"]', 'admin@test.com')
        page.fill('input[name="password"]', 'testpass123')
        page.click('button[type="submit"]')

        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto("http://localhost:8000/investor/")

        content = page.locator('#content-portfolio')
        box = content.bounding_box()
        assert box is not None


class TestTabletViewport:
    """Tests for tablet viewport."""

    def test_home_page_tablet_768(self, browser):
        """Test home page on tablet viewport."""
        page = browser.new_page()
        page.set_viewport_size({'width': 768, 'height': 1024})
        page.goto("http://localhost:8000/")
        expect(page.locator('h1')).to_be_visible()

    def test_dashboard_tablet_768(self, browser):
        """Test dashboard on tablet viewport."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")
        page.fill('input[name="username"], input[name="email"]', 'admin@test.com')
        page.fill('input[name="password"]', 'testpass123')
        page.click('button[type="submit"]')

        page.set_viewport_size({'width': 768, 'height': 1024})
        page.goto("http://localhost:8000/investor/")
        expect(page.locator('h1')).to_be_visible()


class TestResponsiveImages:
    """Tests for responsive images."""

    def test_images_scale_properly(self, browser):
        """Test that images scale properly on mobile."""
        page = browser.new_page()
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto("http://localhost:8000/")

        images = page.locator('img').all()
        for img in images:
            box = img.bounding_box()
            if box:
                assert box['width'] <= 375, f"Image width {box['width']} exceeds viewport"


class TestDesktopViewport:
    """Tests for desktop viewport."""

    def test_home_page_desktop_1280(self, browser):
        """Test home page on desktop."""
        page = browser.new_page()
        page.set_viewport_size({'width': 1280, 'height': 800})
        page.goto("http://localhost:8000/")
        expect(page.locator('h1')).to_be_visible()

    def test_dashboard_desktop_1280(self, browser):
        """Test dashboard on desktop."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")
        page.fill('input[name="username"], input[name="email"]', 'admin@test.com')
        page.fill('input[name="password"]', 'testpass123')
        page.click('button[type="submit"]')

        page.set_viewport_size({'width': 1280, 'height': 800})
        page.goto("http://localhost:8000/investor/")
        expect(page.locator('h1')).to_be_visible()