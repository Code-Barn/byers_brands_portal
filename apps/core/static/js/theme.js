/**
 * Theme Toggle Script
 * Handles light/dark mode switching with localStorage persistence
 */

window.addEventListener("DOMContentLoaded", function () {
  const html = document.documentElement;
  const THEME_KEY = "byers-brands-theme";

  // Get saved theme or OS preference
  const savedTheme = localStorage.getItem(THEME_KEY);
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = savedTheme || (prefersDark ? "dark" : "light");

  // Apply theme
  if (theme === "dark") {
    html.classList.add("dark");
  } else {
    html.classList.remove("dark");
  }

  // Toggle function
  window.toggleTheme = function () {
    if (html.classList.contains("dark")) {
      html.classList.remove("dark");
      localStorage.setItem(THEME_KEY, "light");
    } else {
      html.classList.add("dark");
      localStorage.setItem(THEME_KEY, "dark");
    }
  };
});
