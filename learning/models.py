from django.apps import AppConfig
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from learning.constants import LearningConstants


class LearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'learning'
    verbose_name = 'Learning Management'


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
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text='URL-friendly version of the title',
        allow_unicode=True
    )
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
    level = models.IntegerField(
        null=True,
        blank=True,
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

    logo = models.URLField('logo URL', max_length=255, null=True, blank=True)
    video_url = models.URLField('video URL', max_length=255, null=True, blank=True)

    requirements = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='required_for',
        blank=True,
        verbose_name='Requirements'
    )

    language = models.IntegerField(
        default=1,
        choices=LANGUAGE_CHOICES
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ],
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['slug']),
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
    image = models.URLField('image URL', max_length=255, null=True, blank=True)
    estimated_time = models.PositiveIntegerField()
    is_active = models.BooleanField('active', default=True)

    class Meta:
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_active_lessons(self):
        return self.lessons.filter(is_active=True).order_by('order')
        # Move to manager.py


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

    def __str__(self):
        return f"{self.chapter.title} - {self.title}"

    def get_active_slides(self):
        return self.slides.filter(is_active=True).order_by('order')
        # Move to manager.py


class Editor(models.Model):
    initial_code = models.TextField(
        verbose_name='Initial Code',
        help_text='Default code that will be shown in the editor',
        blank=True
    )

    lang = models.CharField(
        max_length=10,
        choices=LearningConstants.LANGUAGE_CHOICES,
        default='py',
        verbose_name='Programming Language'
    )

    executable = models.BooleanField(
        default=False,
        help_text='Whether the code can be executed in the editor'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Code Editor'
        verbose_name_plural = 'Code Editors'

    def __str__(self):
        return f"{self.get_lang_display()} Editor - {self.initial_code[:50]}"


class BaseQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        (1, 'Single Choice'),
        (2, 'Multiple Choice'),
        (3, 'Text'),
    ]

    title = models.CharField('title', max_length=255)
    description = models.TextField('description')
    question_type = models.IntegerField(choices=QUESTION_TYPE_CHOICES)
    image = models.URLField(max_length=1024, null=True, blank=True)
    video_url = models.URLField(max_length=1024, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    answer_description = models.TextField(help_text='Detailed explanation of the answer')
    editor = models.ForeignKey(
        Editor,
        on_delete=models.CASCADE,
        null=True,
        related_name='editor_for_questions'
    )
    is_text_input = models.BooleanField(
        default=False,
        help_text="If True, answers must be typed rather than selected"
    )

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_multiple_choice(self):
        return self.question_type == 2


class Choice(models.Model):
    CHOICE_TYPE_CHOICES = [
        (1, 'Text Choice'),
        (2, 'Picture Choice'),
        (3, 'None'),
        (4, 'All'),
        (5, 'Other'),
    ]

    question = models.ForeignKey(
        BaseQuestion,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.CharField('text', max_length=255)
    alt_text = models.CharField(max_length=255, null=True, blank=True)
    image = models.URLField(max_length=255, null=True, blank=True)
    order = models.PositiveIntegerField('order')
    hidden = models.BooleanField('hidden', default=False)
    type = models.IntegerField(choices=CHOICE_TYPE_CHOICES)
    is_correct = models.BooleanField(
        default=False,
        help_text="Indicates if this choice is a correct answer"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Choice'
        verbose_name_plural = 'Choices'
        ordering = ['order']

    def __str__(self):
        return f"{self.question.title} - {self.text}"


class Slide(models.Model):
    SLIDE_TYPE_CHOICES = [
        (1, 'Text'),
        (2, 'Quiz'),
    ]

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='slides'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    total_marks = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    type = models.IntegerField(choices=SLIDE_TYPE_CHOICES)
    time_limit = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hints = models.TextField(null=True, blank=True)
    alt_text = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    image = models.URLField(max_length=255, null=True, blank=True)
    video_url = models.URLField(
        max_length=255,
        null=True,
        blank=True
    )
    comments_count = models.PositiveIntegerField(
        default=0
    )
    question = models.ForeignKey(
        BaseQuestion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions_slides'
    )
    editor = models.ForeignKey(
        'users.Staff',
        on_delete=models.SET_NULL,
        null=True,
        related_name='edited_slides'
    )
    order = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Slide'
        verbose_name_plural = 'Slides'

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"
