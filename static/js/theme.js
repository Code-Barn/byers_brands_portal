/**
 * Theme Toggle Script
 * Handles light/dark mode switching with localStorage persistence
 * Brand Color: #0064aa
 */

(function() {
    'use strict';

    const THEME_KEY = 'byers-brands-theme';
    const THEME_DARK = 'dark';
    const THEME_LIGHT = 'light';
    const THEME_SYSTEM = 'system';

    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const htmlElement = document.documentElement;

    /**
     * Get user's system color scheme preference
     */
    function getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches
            ? THEME_DARK
            : THEME_LIGHT;
    }

    /**
     * Get current theme from localStorage or system preference
     */
    function getCurrentTheme() {
        const stored = localStorage.getItem(THEME_KEY);
        if (stored) {
            return stored;
        }
        return getSystemTheme();
    }

    /**
     * Apply theme to the document
     */
    function applyTheme(theme) {
        const isDark = theme === THEME_DARK;

        if (isDark) {
            htmlElement.classList.add('dark');
            themeToggle.setAttribute('aria-label', 'Switch to light mode');
            themeIcon.innerHTML = `
                <path class="sun" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                      style="display: none;"></path>
                <path class="moon" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
            `;
        } else {
            htmlElement.classList.remove('dark');
            themeToggle.setAttribute('aria-label', 'Switch to dark mode');
            themeIcon.innerHTML = `
                <path class="sun" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                      style="display: block;"></path>
                <path class="moon" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                      style="display: none;"></path>
            `;
        }

        // Store preference
        localStorage.setItem(THEME_KEY, theme);
    }

    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
        const current = getCurrentTheme();
        const next = current === THEME_DARK ? THEME_LIGHT : THEME_DARK;
        applyTheme(next);
    }

    /**
     * Watch for system theme changes
     */
    function watchSystemTheme() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

        mediaQuery.addEventListener('change', (event) => {
            // Only apply system theme if user hasn't explicitly chosen
            const stored = localStorage.getItem(THEME_KEY);
            if (!stored || stored === THEME_SYSTEM) {
                applyTheme(event.matches ? THEME_DARK : THEME_LIGHT);
            }
        });
    }

    /**
     * Initialize theme system
     */
    function initTheme() {
        // Set initial theme
        const theme = getCurrentTheme();
        applyTheme(theme);

        // Watch for system preference changes
        watchSystemTheme();

        // Set up toggle button
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                toggleTheme();
            });

            // Set initial ARIA attributes
            themeToggle.setAttribute('role', 'button');
            themeToggle.setAttribute('aria-pressed',
                htmlElement.classList.contains('dark') ? 'true' : 'false');
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
})();
