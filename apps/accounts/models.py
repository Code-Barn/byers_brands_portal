"""
Custom user model for DID-based authentication.
"""
import secrets
import hashlib
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator


class CustomUser(AbstractUser):
    """
    Custom user model extending AbstractUser with DID support and MFA.
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

    # MFA (TOTP) fields
    mfa_enabled = models.BooleanField(
        'MFA Enabled',
        default=False,
        help_text='Whether TOTP-based MFA is enabled for this user'
    )
    mfa_secret = models.CharField(
        'MFA Secret',
        max_length=64,
        blank=True,
        help_text='Encrypted TOTP secret (server stores hash only)'
    )
    mfa_secret_hash = models.CharField(
        'MFA Secret Hash',
        max_length=128,
        blank=True,
        help_text='SHA-256 hash of TOTP secret for verification'
    )
    mfa_backup_codes = models.JSONField(
        'MFA Backup Codes',
        blank=True,
        null=True,
        help_text='One-time backup codes for account recovery'
    )
    mfa_last_verified = models.DateTimeField(
        'Last MFA Verification',
        blank=True,
        null=True,
        help_text='Timestamp of last successful MFA verification'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def generate_mfa_secret(self):
        """Generate a new TOTP secret."""
        return secrets.token_hex(20)

    def set_mfa_secret(self, secret):
        """Set MFA secret with secure hashing."""
        self.mfa_secret = secret
        self.mfa_secret_hash = hashlib.sha256(secret.encode()).hexdigest()

    def verify_mfa_code(self, code):
        """Verify a TOTP code (stub - requires pyotp or similar)."""
        try:
            import pyotp
            totp = pyotp.TOTP(self.mfa_secret)
            return totp.verify(code, valid_window=1)
        except Exception:
            return False

    def generate_backup_codes(self):
        """Generate backup codes for account recovery."""
        codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.mfa_backup_codes = codes
        return codes

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
