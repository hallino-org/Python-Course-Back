from django.core.exceptions import ValidationError
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

    def get_active_chapters(self):
        return self.chapters.filter(is_active=True).order_by('order')


class Chapter(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='chapters'
    )
    title = models.CharField('title', max_length=255)
    description = models.TextField('description')
    order = models.PositiveIntegerField('order')
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)
    image = models.URLField('image URL', max_length=255)
    estimated_time = models.PositiveIntegerField()
    is_active = models.BooleanField('active', default=True)

    class Meta:
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_active_lessons(self):
        """Get all active lessons ordered by their order"""
        return self.lessons.filter(is_active=True).order_by('order')


class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        (1, 'Lesson'),
        (2, 'Quiz'),
    ]

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField('title', max_length=255)
    description = models.TextField('description')
    order = models.PositiveIntegerField('order')
    duration = models.PositiveIntegerField(
        'duration',
        help_text='Duration in minutes'
    )
    is_required = models.BooleanField('required', default=True)
    is_active = models.BooleanField('active', default=True)
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)
    score = models.PositiveIntegerField('score')
    lesson_type = models.IntegerField(
        'lesson type',
        choices=LESSON_TYPE_CHOICES
    )

    class Meta:
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['chapter', 'order']
        unique_together = ['chapter', 'order']

    def __str__(self):
        return f"{self.chapter.title} - {self.title}"


class BaseQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        (1, 'Choice'),
        (2, 'Text'),
    ]

    title = models.CharField('title', max_length=255)
    description = models.TextField('description')
    question_type = models.IntegerField(
        choices=QUESTION_TYPE_CHOICES
    )
    image = models.URLField(
        max_length=1024,
        null=True,
        blank=True
    )
    video_url = models.URLField(
        max_length=1024,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    answer_description = models.TextField(
        help_text='Detailed explanation of the answer'
    )
    editor = models.ForeignKey(
        'users.Staff',
        on_delete=models.SET_NULL,
        null=True,
        related_name='edited_questions'
    )

    class Meta:
        verbose_name = 'Base question'
        verbose_name_plural = 'Base questions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if not self.image and not self.description:
            raise ValidationError('Either image or description must be provided')


class ChoiceQuestion(BaseQuestion):
    is_multiselect = models.BooleanField(default=False)
    correct_choices = models.ManyToManyField(
        'Choice',
        related_name='correct_for_questions'
    )

    class Meta:
        verbose_name = 'Choice question'
        verbose_name_plural = 'Choice questions'

    def clean(self):
        super().clean()
        if self.question_type != 1:  # Choice type
            raise ValidationError('Question type must be Choice for ChoiceQuestion')

        # Validate correct choices count
        if not self.is_multiselect and self.correct_choices.count() > 1:
            raise ValidationError('Single-select questions can only have one correct answer')


class Choice(models.Model):
    CHOICE_TYPE_CHOICES = [
        (1, 'Text Choice'),
        (2, 'Picture Choice'),
        (3, 'None'),
        (4, 'All'),
        (5, 'Other'),
    ]

    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField('text', max_length=255)
    alt_text = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    image = models.URLField(
        max_length=255,
        null=True,
        blank=True
    )
    order = models.PositiveIntegerField('order')
    hidden = models.BooleanField('hidden', default=False)
    type = models.IntegerField(choices=CHOICE_TYPE_CHOICES)

    class Meta:
        verbose_name = 'Choice'
        verbose_name_plural = 'Choices'
        ordering = ['question', 'order']
        unique_together = ['question', 'order']

    def __str__(self):
        return f"{self.question.title} - {self.text}"

    def clean(self):
        super().clean()
        if self.type == 2 and not self.image:
            raise ValidationError('Image is required for picture choices')

        if self.image and not self.alt_text:
            raise ValidationError('Alternative text is required when image is provided')
