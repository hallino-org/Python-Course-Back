from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Category(models.Model):
    title = models.CharField('title', max_length=255)
    description = models.TextField('description')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    LEVEL_CHOICES = [
        (1, 'Elementary'),
        (2, 'Intermediate'),
        (3, 'Upper Intermediate'),
        (4, 'Advanced'),
    ]

    LANGUAGE_CHOICES = [
        (1, 'Fa'),
        (2, 'En'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    authors = models.ManyToManyField(
        'users.Author',
        related_name='courses',
        verbose_name='Authors'
    )
    categories = models.ManyToManyField(
        Category,
        related_name='courses',
        verbose_name='Categories'
    )
    duration = models.PositiveIntegerField()
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price in Rials'
    )
    start_date = models.DateField(
        null=True,
        blank=True
    )
    end_date = models.DateField(
        null=True,
        blank=True
    )
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    logo = models.URLField('logo URL', max_length=255)
    video_url = models.URLField('video URL', max_length=255)

    requirements = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='required_for',
        blank=True,
        verbose_name='Requirements'
    )

    language = models.IntegerField(
        choices=LANGUAGE_CHOICES
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ],
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['level']),
            models.Index(fields=['is_published', 'is_active']),
        ]

    def __str__(self):
        return self.title

    def calculate_rating(self):
        """Calculate average rating based on user reviews"""
        pass
