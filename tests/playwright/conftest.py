"""
Playwright configuration and fixtures for Byers Brands Portal tests.
"""
import os
import sys
import re
from pathlib import Path

import pytest
from django.test import Client
from django.contrib.auth import get_user_model

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')


@pytest.fixture(scope='session')
def browser():
    """Launch a browser for tests."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def django_client():
    """Django test client fixture."""
    return Client()


@pytest.fixture
def authenticated_client(django_client):
    """Django client with authenticated user."""
    User = get_user_model()
    user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )
    django_client.force_login(user)
    return django_client


@pytest.fixture
def user_with_did():
    """User with DID for authentication tests."""
    User = get_user_model()
    user = User.objects.create_user(
        email='did@example.com',
        username='diduser',
        password='testpass123',
        did='did:key:z6Mktest123',
        did_document={'id': 'did:key:z6Mktest123', 'type': 'DIDDocument'}
    )
    return user


@pytest.fixture
def base_url():
    """Base URL for tests."""
    return os.environ.get('TEST_BASE_URL', 'http://localhost:8000')


@pytest.fixture
def theme():
    """Get current theme preference."""
    return 'light'


@pytest.fixture
def polly_api_url():
    """Polly API URL for tests."""
    return os.environ.get('POLLY_API_URL', 'http://localhost:8001')


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line('markers', 'slow: marks tests as slow')
    config.addinivalue_line('markers', 'auth: marks tests requiring authentication')
    config.addinivalue_line('markers', 'polly: marks tests requiring Polly integration')