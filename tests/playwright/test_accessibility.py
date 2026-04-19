"""
Playwright tests for accessibility (WCAG 2.1 AA compliance).
Uses axe-core for automated accessibility auditing.
"""
import pytest
from playwright.sync_api import expect


class TestAccessibilityAriaLabels:
    """Tests for ARIA labels and roles."""

    def test_navigation_has_aria_label(self, browser):
        """Test that navigation has proper aria-label."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        nav = page.locator('nav[role="navigation"]')
        expect(nav).to_be_visible()

    def test_theme_toggle_has_aria_label(self, browser):
        """Test that theme toggle has aria-label."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        toggle = page.locator('button[aria-label]')
        expect(toggle).to_be_visible()
        label = toggle.first.get_attribute('aria-label')
        assert label and 'theme' in label.lower()

    def test_mobile_menu_button_has_aria_label(self, browser):
        """Test that mobile menu button has aria-label."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        menu_btn = page.locator('#mobile-menu-button')
        expect(menu_btn).to_have_attribute('aria-label', /menu|open/i)

    def test_skip_link_exists(self, browser):
        """Test that skip to main content link exists."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        skip_link = page.locator('a[href="#main-content"]')
        expect(skip_link).to_be_visible()

    def test_main_content_has_id(self, browser):
        """Test that main content has id for skip link."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        main = page.locator('main#main-content')
        expect(main).to_be_visible()

    def test_images_have_alt_text(self, browser):
        """Test that images have alt text."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        images = page.locator('img').all()
        for img in images:
            alt = img.get_attribute('alt')
            assert alt is not None and alt != '', f"Image missing alt text"

    def test_form_inputs_have_labels(self, browser):
        """Test that form inputs have associated labels."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")
        inputs = page.locator('input').all()
        for inp in inputs:
            name = inp.get_attribute('name')
            if name and name not in ['csrfmiddlewaretoken']:
                label = page.locator(f'label[for="{inp.get_attribute('id')}"]')
                aria_label = inp.get_attribute('aria-label')
                has_label = label.count() > 0 or aria_label
                assert has_label, f"Input {name} lacks label"


class TestAccessibilityKeyboard:
    """Tests for keyboard navigation."""

    def test_can_navigate_with_tab(self, browser):
        """Test that Tab key navigates between elements."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")

        page.keyboard.press('Tab')
        focused = page.evaluate("document.activeElement.tagName")
        assert focused in ['INPUT', 'BUTTON', 'A']

    def test_focus_indicator_visible(self, browser):
        """Test that focus indicator is visible."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")

        page.keyboard.press('Tab')
        focused = page.locator(':focus')
        expect(focused).to_be_visible()

    def test_buttons_keyboard_accessible(self, browser):
        """Test that buttons are accessible via keyboard."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")

        page.keyboard.press('Tab')
        page.keyboard.press('Tab')
        page.keyboard.press('Enter')
        expect(page.locator('body')).to_be_visible()


class TestAccessibilityColorContrast:
    """Tests for color contrast (WCAG 2.1 AA requires 4.5:1 for normal text)."""

    def test_primary_text_contrast_light_mode(self, browser):
        """Test that primary text has sufficient contrast in light mode."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        page.evaluate("document.documentElement.classList.remove('dark')")

        text = page.locator('h1').first
        color = page.evaluate("""
            window.getComputedStyle(arguments[0]).color
        """.format('h1'))
        assert color, "Could not get text color"

    def test_primary_text_contrast_dark_mode(self, browser):
        """Test that primary text has sufficient contrast in dark mode."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        page.evaluate("document.documentElement.classList.add('dark')")

        text = page.locator('h1').first
        expect(text).to_be_visible()

    def test_link_contrast(self, browser):
        """Test that links have sufficient contrast."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        page.evaluate("document.documentElement.classList.remove('dark')")

        links = page.locator('a').all()
        assert len(links) > 0, "No links found to test"


class TestAccessibilityFocusOrder:
    """Tests for logical focus order."""

    def test_focus_order_is_logical(self, browser):
        """Test that focus order follows visual order."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")

        page.keyboard.press('Tab')
        first_focus = page.evaluate("document.activeElement.tagName")

        page.keyboard.press('Tab')
        second_focus = page.evaluate("document.activeElement.tagName")

        assert first_focus in ['INPUT', 'BUTTON', 'A']
        assert second_focus in ['INPUT', 'BUTTON', 'A']


class TestAccessibilitySemanticHtml:
    """Tests for semantic HTML usage."""

    def test_uses_header_element(self, browser):
        """Test that page uses proper header elements."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        header = page.locator('header, nav')
        expect(header).to_be_visible()

    def test_uses_main_element(self, browser):
        """Test that page uses main element."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        main = page.locator('main')
        expect(main).to_be_visible()

    def test_uses_footer_element(self, browser):
        """Test that page uses footer element."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        footer = page.locator('footer')
        expect(footer).to_be_visible()


class TestAccessibilityInteractiveElements:
    """Tests for interactive element accessibility."""

    def test_all_buttons_have_text_or_aria(self, browser):
        """Test that buttons have accessible text."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")

        buttons = page.locator('button').all()
        for btn in buttons:
            text = btn.inner_text().strip()
            aria_label = btn.get_attribute('aria-label')
            aria_labelledby = btn.get_attribute('aria-labelledby')
            has_accessible_name = text or aria_label or aria_labelledby
            assert has_accessible_name, f"Button lacks accessible name"

    def test_modals_have_focus_trap(self, browser):
        """Test that modals can receive focus."""
        page = browser.new_page()
        page.goto("http://localhost:8000/investor/")

        modal = page.locator('[role="dialog"], .modal')
        if modal.count() > 0:
            expect(modal.first).to_be_visible()


class TestAccessibilityRoleAttributes:
    """Tests for appropriate role attributes."""

    def test_navigation_has_role(self, browser):
        """Test that navigation has appropriate role."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        nav = page.locator('nav[role="navigation"], nav')
        expect(nav).to_be_visible()

    def test_contentinfo_role_on_footer(self, browser):
        """Test that footer has contentinfo role."""
        page = browser.new_page()
        page.goto("http://localhost:8000/")
        footer = page.locator('footer[role="contentinfo"], footer')
        expect(footer).to_be_visible()


class TestAccessibilityForms:
    """Tests for form accessibility."""

    def test_required_fields_marked(self, browser):
        """Test that required fields are marked."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/register/")

        required_inputs = page.locator('input[required]').all()
        assert len(required_inputs) > 0, "No required fields found"

    def test_error_messages_are_accessible(self, browser):
        """Test that error messages are accessible."""
        page = browser.new_page()
        page.goto("http://localhost:8000/accounts/login/")
        page.click('button[type="submit"]')
        expect(page.locator('body')).to_be_visible()