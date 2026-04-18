"""
Investor models for portfolio tracking, documents, and investment opportunities.
"""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class InvestmentStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    CLOSED = 'closed', 'Closed'
    PENDING = 'pending', 'Pending'


class DocumentType(models.TextChoices):
    TAX = 'tax', 'Tax Document'
    STATEMENT = 'statement', 'Statement'
    CONTRACT = 'contract', 'Contract'
    REPORT = 'report', 'Report'
    OTHER = 'other', 'Other'


class OpportunityStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    FUNDED = 'funded', 'Funded'
    CLOSED = 'closed', 'Closed'
    EXPIRED = 'expired', 'Expired'


class Investment(models.Model):
    """Individual investment in user's portfolio."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='investments'
    )
    name = models.CharField(max_length=255, help_text='Name of the investment')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Initial investment amount'
    )
    current_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Current value of the investment'
    )
    date_invested = models.DateField(help_text='Date of initial investment')
    returns_percentage = models.FloatField(
        default=0.0,
        help_text='Percentage return on investment'
    )
    status = models.CharField(
        max_length=20,
        choices=InvestmentStatus.choices,
        default=InvestmentStatus.ACTIVE
    )
    notes = models.TextField(blank=True, help_text='Additional notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - ${self.amount}"


class Portfolio(models.Model):
    """Portfolio summary for a user."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='portfolio'
    )
    total_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total portfolio value'
    )
    total_invested = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total amount invested'
    )
    total_returns = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Total returns earned'
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

    def __str__(self):
        return f"Portfolio: {self.user.email}"

    def update_totals(self):
        """Recalculate portfolio totals from investments."""
        investments = self.user.investments.filter(status=InvestmentStatus.ACTIVE)
        self.total_invested = sum(inv.amount for inv in investments)
        self.total_value = sum(inv.current_value for inv in investments)
        self.total_returns = self.total_value - self.total_invested
        self.save()


class Document(models.Model):
    """Document storage for investor documents."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField(max_length=255, help_text='Document title')
    file = models.FileField(
        upload_to='investor_documents/%Y/%m/',
        help_text='Uploaded file'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER
    )
    description = models.TextField(blank=True, help_text='Document description')
    file_size = models.PositiveIntegerField(
        default=0,
        help_text='File size in bytes'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class InvestmentOpportunity(models.Model):
    """Investment opportunities available to investors."""
    title = models.CharField(max_length=255, help_text='Opportunity title')
    description = models.TextField(help_text='Detailed description')
    min_investment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Minimum investment amount'
    )
    max_investment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Maximum investment amount'
    )
    expected_returns_percentage = models.FloatField(
        help_text='Expected annual returns percentage'
    )
    status = models.CharField(
        max_length=20,
        choices=OpportunityStatus.choices,
        default=OpportunityStatus.AVAILABLE
    )
    deadline = models.DateField(
        blank=True,
        null=True,
        help_text='Application deadline'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title