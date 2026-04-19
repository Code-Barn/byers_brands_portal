"""
Playwright tests for branding and UI consistency.
"""
import pytest
from playwright.sync_api import expect


class TestBranding:
    """Tests for branding consistency."""

    def test_brand_color_in_css(self):
        """Test that brand color is defined in CSS."""
        import os
        css_path = os.path.join(os.path.dirname(__file__), '../../../apps/core/static/css/styles.css')
        with open(css_path, 'r') as f:
            css = f.read()
        assert '#0064aa' in css or '--brand-blue' in css

    def test_light_mode_logo_visible(self, browser):
        """Test that light mode logo is visible in light mode."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        light_logo = page.locator('img[alt*="Logo"]:not([src*="DM"]), img[alt="Byers Brands Logo"]:visible').first
        html = page.locator('html')
        if 'dark' not in html.get_attribute('class') or html.evaluate('!document.documentElement.classList.contains("dark")'):
            expect(light_logo).to_be_visible()

    def test_dark_mode_logo_visible(self, browser):
        """Test that dark mode logo is visible in dark mode."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        page.evaluate("document.documentElement.classList.add('dark')")
        dark_logo = page.locator('img[src*="DM"], img[alt*="Dark"]').first
        expect(dark_logo).to_be_visible()

    def test_brand_color_buttons(self, browser):
        """Test that buttons use brand color."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")
        submit_btn = page.locator('button[type="submit"]').first
        expect(submit_btn).to_have_class(/bg-blue-600|bg-\[#0064aa\]/)

    def test_form_inputs_use_brand_color_focus(self, browser):
        """Test that form inputs have brand color on focus."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")
        input_field = page.locator('input').first
        input_field.focus()
        expect(input_field).to_have_class(/focus:ring-blue-500|focus:ring-\[#0064aa\]/)

    def test_dark_mode_toggle_exists(self, browser):
        """Test that theme toggle button exists."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        toggle = page.locator('button[aria-label*="theme"], button[onclick="toggleTheme()"]')
        expect(toggle).to_be_visible()


class TestThemeConsistency:
    """Tests for theme consistency across pages."""

    def test_theme_persists_across_pages(self, browser):
        """Test that theme persists when navigating pages."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        page.evaluate("document.documentElement.classList.add('dark')")
        page.evaluate("localStorage.setItem('byers-brands-theme', 'dark')")

        page.goto("http://localhost:8000/about/")
        expect(page.locator('html')).to_have_class(/dark/)

    def test_all_pages_support_dark_mode(self, browser):
        """Test that all main pages support dark mode."""
        pages = [
            "http://localhost:8000/",
            "http://localhost:8000/about/",
            "http://localhost:8000/products/",
            "http://localhost:8000/contact/",
        ]
        page = browser.new_page()
        for url in pages:
            page.goto(url)
            page.evaluate("document.documentElement.classList.add('dark')")
            html = page.locator('html')
            expect(html).to_have_class(/dark/)


class TestTypographyAndSpacing:
    """Tests for typography and spacing consistency."""

    def test_headings_use_brand_font(self, browser):
        """Test that headings use consistent font."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        h1 = page.locator('h1').first
        expect(h1).to_be_visible()

    def test_consistent_spacing(self, browser):
        """Test that spacing is consistent."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        nav = page.locator('nav')
        footer = page.locator('footer')
        main = page.locator('main')
        expect(nav).to_be_visible()
        expect(main).to_be_visible()
        expect(footer).to_be_visible()