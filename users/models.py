# users/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def _validate_user_data(self, email, username):
        if not email:
            raise ValueError('The Email field must be set')

        if not username:
            raise ValueError('The Username field must be set')

        # Case-insensitive email check
        email = self.normalize_email(email)
        if self.model.objects.filter(email__iexact=email).exists():
            raise ValueError('User with this email already exists')

        # Case-insensitive username check
        username = username.lower()
        if self.model.objects.filter(username__iexact=username).exists():
            raise ValueError('User with this username already exists')

        return email, username

    def create_user(self, email, username, password=None, **extra_fields):
        email, username = self._validate_user_data(email, username)

        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_confirmed', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        (1, 'female'),
        (2, 'male'),
    ]

    USER_TYPE_CHOICES = [
        (1, 'free'),
        (2, 'pro'),
    ]

    LEVEL_CHOICES = [
        (1, 'basic'),
        (2, 'advanced'),
    ]

    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': "A user with that email already exists.",
        }
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            'unique': "A user with that username already exists.",
        }
    )

    firstname = models.CharField(max_length=150)

    lastname = models.CharField(max_length=150)

    gender = models.IntegerField(choices=GENDER_CHOICES, default=1)

    phone_number = PhoneNumberField()

    birth_date = models.DateField(null=True, blank=True)

    type = models.IntegerField(choices=USER_TYPE_CHOICES, default=1)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=1)

    is_active = models.BooleanField(default=True)
    is_confirmed = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expire_date = models.DateField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'firstname', 'lastname', 'phone_number']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name='unique_email_case_insensitive',
            ),
            models.UniqueConstraint(
                fields=['username'],
                name='unique_username_case_insensitive',
            ),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.firstname} {self.lastname}'

    def has_valid_subscription(self):
        if not self.expire_date:
            return False
        return self.expire_date >= timezone.now().date()

    def get_role(self):
        if hasattr(self, 'staff'):
            return dict(Staff.ROLE_CHOICES)[self.staff.role_type]
        if hasattr(self, 'author_profile'):
            return 'author'
        return 'student'


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(help_text="Author's biography", null=True, blank=True)
    specializations = models.JSONField(default=list, help_text="List of areas of expertise", null=True, blank=True)
    total_courses = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.full_name

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

        ordering = ['-total_courses']

    def get_active_courses(self):
        """Get author's active courses"""
        return self.course_set.filter(is_active=True)  # Create this latter


class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('learning.Course', on_delete=models.CASCADE)  # Create this later
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    score = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rank = models.IntegerField()

    class Meta:
        verbose_name = 'User course'
        verbose_name_plural = 'User courses'
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.full_name} - {self.course}"


class Streak(models.Model):
    STREAK_TYPE_CHOICES = [
        (7, '7 days'),
        (14, '14 days'),
        (30, '30 days'),
        (90, '90 days'),
        (120, '120 days'),
        (365, '365 days'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_interaction = models.DateField()
    current_streak = models.IntegerField(default=0)
    type = models.IntegerField(choices=STREAK_TYPE_CHOICES)
    highest_streak = models.IntegerField('highest streak', default=0)

    class Meta:
        verbose_name = 'Streak'
        verbose_name_plural = 'Streaks'
        unique_together = ['user', 'type']

    def update_streak(self, interaction_date=None):
        if interaction_date is None:
            interaction_date = timezone.now().date()

        if not self.last_interaction:
            self.current_streak = 1
        else:
            days_diff = (interaction_date - self.last_interaction).days
            if days_diff == 1:  # consecutive day
                self.current_streak += 1
            elif days_diff > 1:  # streak broken
                self.current_streak = 1

        self.last_interaction = interaction_date
        self.highest_streak = max(self.highest_streak, self.current_streak)
        self.save()


class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('learning.Question', on_delete=models.CASCADE)  # Create this later
    text_answer = models.JSONField(default=list, null=True, blank=True)
    choice_answer = models.JSONField(default=list, null=True, blank=True)
    submitted_at = models.DateTimeField('submitted at', auto_now_add=True)

    class Meta:
        verbose_name = 'User response'
        verbose_name_plural = 'User responses'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.question}"


class Staff(models.Model):
    ROLE_CHOICES = [
        (1, 'admin'),
        (2, 'accounting'),
        (3, 'support'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role_type = models.IntegerField(choices=ROLE_CHOICES)
