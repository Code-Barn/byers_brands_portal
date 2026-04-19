"""
Feedback model for user-submitted UI/UX suggestions and bug reports.
"""
from django.contrib.auth import get_user_model
from django.db import models


class FeedbackCategory(models.TextChoices):
    SUGGESTION = 'suggestion', 'UI/UX Suggestion'
    BUG = 'bug', 'Bug Report'
    FEATURE = 'feature', 'Feature Request'
    OTHER = 'other', 'Other'


class FeedbackStatus(models.TextChoices):
    NEW = 'new', 'New'
    REVIEWED = 'reviewed', 'Reviewed'
    RESOLVED = 'resolved', 'Resolved'
    REJECTED = 'rejected', 'Rejected'


class Feedback(models.Model):
    """User feedback for UI/UX improvements."""
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='feedbacks',
        help_text='User who submitted the feedback'
    )
    category = models.CharField(
        max_length=20,
        choices=FeedbackCategory.choices,
        default=FeedbackCategory.SUGGESTION,
        help_text='Type of feedback'
    )
    subject = models.CharField(
        max_length=255,
        help_text='Brief subject of the feedback'
    )
    message = models.TextField(
        help_text='Detailed feedback message'
    )
    screenshot = models.FileField(
        upload_to='feedback/screenshots/%Y/%m/',
        blank=True,
        null=True,
        help_text='Optional screenshot of the issue'
    )
    url_context = models.CharField(
        max_length=500,
        blank=True,
        help_text='URL where the feedback was submitted from'
    )
    status = models.CharField(
        max_length=20,
        choices=FeedbackStatus.choices,
        default=FeedbackStatus.NEW,
        help_text='Status of the feedback'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text='Internal notes for admins'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

    def __str__(self):
        return f"{self.category}: {self.subject} ({self.get_status_display()})"