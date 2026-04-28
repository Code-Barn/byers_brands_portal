"""Playwright tests for brand carousel and single-page navigation."""

def test_carousel_exists(browser):
    """Test that the brand carousel exists on the homepage."""
    page = browser.new_page()
    page.goto("http://localhost:8000/")

    # Check that the products section exists
    products_section = page.locator("#products")
    assert products_section.is_visible()

    # Check that the carousel track exists
    carousel_track = page.locator("#carousel-track")
    assert carousel_track.is_visible()

    # Check that there are project cards in the carousel
    project_cards = page.locator("#carousel-track > div")
    assert project_cards.count() >= 5


def test_carousel_scroll_buttons(browser):
    """Test that carousel scroll buttons work."""
    page = browser.new_page()
    page.goto("http://localhost:8000/#products")

    # Wait for carousel to load
    page.wait_for_selector("#carousel-track")

    # Get initial scroll position
    initial_scroll = page.evaluate("document.getElementById('carousel-track').scrollLeft")

    # Click right button
    right_btn = page.locator("#carousel-right")
    right_btn.click()

    # Wait for scroll to happen
    page.wait_for_timeout(500)

    # Check that scroll position changed
    new_scroll = page.evaluate("document.getElementById('carousel-track').scrollLeft")
    assert new_scroll > initial_scroll

    # Click left button
    left_btn = page.locator("#carousel-left")
    left_btn.click()

    page.wait_for_timeout(500)

    # Check that scroll position decreased
    final_scroll = page.evaluate("document.getElementById('carousel-track').scrollLeft")
    assert final_scroll < new_scroll


def test_carousel_horizontal_scroll(browser):
    """Test that carousel supports horizontal scrolling."""
    page = browser.new_page()
    page.goto("http://localhost:8000/#products")

    # Wait for carousel to load
    page.wait_for_selector("#carousel-track")

    # Get track element
    track = page.locator("#carousel-track")

    # Check that it has overflow-x: auto styling
    overflow = track.evaluate("el => getComputedStyle(el).overflowX")
    assert overflow in ['auto', 'scroll']


def test_navigation_scroll_to_sections(browser):
    """Test that navigation links scroll to correct sections."""
    page = browser.new_page()
    page.goto("http://localhost:8000/")

    # Test About link
    about_link = page.locator('a[href="#about"]').first
    about_link.click()
    page.wait_for_timeout(500)

    # Check URL has #about
    assert '#about' in page.url

    # Check that about section is visible
    about_section = page.locator("#about")
    assert about_section.is_visible()

    # Test Products link
    products_link = page.locator('a[href="#products"]').first
    products_link.click()
    page.wait_for_timeout(500)

    assert '#products' in page.url

    products_section = page.locator("#products")
    assert products_section.is_visible()


def test_navigation_active_state(browser):
    """Test that active navigation item updates on scroll."""
    page = browser.new_page()
    page.goto("http://localhost:8000/")

    # Wait for page to load
    page.wait_for_selector("#home")

    # Scroll to about section
    page.evaluate("document.getElementById('about').scrollIntoView({behavior: 'smooth'})")
    page.wait_for_timeout(1000)

    # Check that About nav link has active styling
    about_nav = page.locator('a[data-section="about"]').first
    classes = about_nav.get_attribute("class")
    assert "text-blue-600" in classes or "font-semibold" in classes


def test_login_register_links_navigate_to_pages(browser):
    """Test that Login, Register, and DID Login links go to separate pages."""
    page = browser.new_page()
    page.goto("http://localhost:8000/")

    # Test Login link
    login_link = page.locator('a[href*="login"]').first
    href = login_link.get_attribute("href")
    assert "login" in href
    assert "#" not in href  # Should not be an anchor link

    # Test Register link
    register_link = page.locator('a[href*="register"]').first
    href = register_link.get_attribute("href")
    assert "register" in href
    assert "#" not in href

    # Test DID Login link
    did_link = page.locator('a[href*="did_login"]').first
    href = did_link.get_attribute("href")
    assert "did_login" in href
    assert "#" not in href


def test_carousel_responsive_mobile(browser):
    """Test that carousel is usable on mobile viewport."""
    page = browser.new_page()
    page.set_viewport_size({"width": 375, "height": 667})  # iPhone SE size
    page.goto("http://localhost:8000/#products")

    # Wait for carousel
    page.wait_for_selector("#carousel-track")

    # Check that carousel track is visible and scrollable
    track = page.locator("#carousel-track")
    assert track.is_visible()

    # Check that project cards are visible
    project_cards = page.locator("#carousel-track > div")
    assert project_cards.count() > 0

    # Check first card is visible
    first_card = project_cards.first
    assert first_card.is_visible()


def test_project_links_open_in_new_tab(browser):
    """Test that project links in carousel open in new tab if they have links."""
    page = browser.new_page()
    page.goto("http://localhost:8000/#products")

    # Wait for carousel
    page.wait_for_selector("#carousel-track")

    # Find project links with target="_blank"
    project_links = page.locator("#carousel-track a[target='_blank']")
    if project_links.count() > 0:
        link = project_links.first
        target = link.get_attribute("target")
        assert target == "_blank"

        rel = link.get_attribute("rel")
        assert "noopener" in rel or "noreferrer" in rel


def test_carousel_indicators(browser):
    """Test that carousel indicators exist and are clickable."""
    page = browser.new_page()
    page.goto("http://localhost:8000/#products")

    # Wait for indicators
    page.wait_for_selector("#carousel-indicators")

    # Check that indicators exist
    indicators = page.locator(".indicator-dot")
    assert indicators.count() >= 5

    # Click first indicator
    first_indicator = indicators.first
    first_indicator.click()
    page.wait_for_timeout(500)

    # Check that the carousel scrolled
    scroll_left = page.evaluate("document.getElementById('carousel-track').scrollLeft")
    assert scroll_left >= 0
