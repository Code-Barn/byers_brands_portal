/**
 * Mobile Menu Toggle Script
 * Handles mobile navigation menu toggle
 */

(function() {
    'use strict';

    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    function initMobileMenu() {
        if (!mobileMenuButton || !mobileMenu) {
            return;
        }

        // Set initial ARIA attributes
        mobileMenuButton.setAttribute('aria-expanded', 'false');
        mobileMenuButton.setAttribute('aria-controls', 'mobile-menu');
        mobileMenuButton.setAttribute('aria-label', 'Open mobile menu');
        mobileMenu.setAttribute('aria-hidden', 'true');

        // Toggle menu on button click
        mobileMenuButton.addEventListener('click', function() {
            const isExpanded = mobileMenuButton.getAttribute('aria-expanded') === 'true';

            if (isExpanded) {
                // Close menu
                mobileMenuButton.setAttribute('aria-expanded', 'false');
                mobileMenuButton.setAttribute('aria-label', 'Open mobile menu');
                mobileMenu.setAttribute('aria-hidden', 'true');
            } else {
                // Open menu
                mobileMenuButton.setAttribute('aria-expanded', 'true');
                mobileMenuButton.setAttribute('aria-label', 'Close mobile menu');
                mobileMenu.setAttribute('aria-hidden', 'false');
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (mobileMenuButton.getAttribute('aria-expanded') === 'true') {
                if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
                    mobileMenuButton.setAttribute('aria-expanded', 'false');
                    mobileMenuButton.setAttribute('aria-label', 'Open mobile menu');
                    mobileMenu.setAttribute('aria-hidden', 'true');
                }
            }
        });

        // Close menu when a link is clicked
        const menuLinks = mobileMenu.querySelectorAll('a[href]');
        menuLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuButton.setAttribute('aria-expanded', 'false');
                mobileMenuButton.setAttribute('aria-label', 'Open mobile menu');
                mobileMenu.setAttribute('aria-hidden', 'true');
            });
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileMenu);
    } else {
        initMobileMenu();
    }
})();
