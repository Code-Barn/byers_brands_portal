"""
Core app - shared resources for Byers Brands
Contains base templates, static files (CSS, JS, images), and common functionality.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core Resources'
