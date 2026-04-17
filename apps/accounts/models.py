"""
Custom user model for DID-based authentication.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator


class CustomUser(AbstractUser):
    """
    Custom user model extending AbstractUser with DID support.
    Uses email as the primary identifier instead of username.
    """
    email = models.EmailField(
        'Email Address',
        unique=True,
        validators=[EmailValidator(message='Enter a valid email address.')]
    )
    did = models.CharField(
        'Decentralized Identifier',
        max_length=255,
        blank=True,
        null=True,
        help_text='User DID (e.g., did:key:z6MkqRYqQiSgvZQdnBytw86Qbs2ZWUkGv22od...)'
    )
    did_document = models.JSONField(
        'DID Document',
        blank=True,
        null=True,
        help_text='Full DID document as JSON'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
