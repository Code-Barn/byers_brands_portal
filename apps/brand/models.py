"""Models for Brand app."""
from django.db import models


class BrandPage(models.Model):
    """Model for static brand pages."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(blank=True)
    description = models.CharField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Brand Page'
        verbose_name_plural = 'Brand Pages'

    def __str__(self):
        return self.title


class Product(models.Model):
    """Model for products."""
    name = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    category = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name


class Project(models.Model):
    """Ecosystem projects (Polly, Namechart, etc.)."""
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='project_logos/', blank=True)
    description = models.CharField(max_length=500)
    link = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Ecosystem Project'
        verbose_name_plural = 'Ecosystem Projects'

    def __str__(self):
        return self.name
