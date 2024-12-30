from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

import learning.models


class UserManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, phone_number, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            firstname=firstname,
            lastname=lastname,
            phone_number=phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, phone_number, password=None):
        user = self.create_user(
            email=email,
            firstname=firstname,
            lastname=lastname,
            phone_number=phone_number,
            password=password,
        )
        user.is_staff = True
        user.is_confirmed = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    GENDER_CHOICES = [
        (1, 'female'),
        (2, 'male'),
        (3, 'None')
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

    firstname = models.CharField(max_length=150)

    lastname = models.CharField(max_length=150)

    gender = models.IntegerField(choices=GENDER_CHOICES, default=3)

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
    REQUIRED_FIELDS = ['firstname', 'lastname', 'phone_number']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.firstname} {self.lastname}'

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    def get_username(self):
        return self.email


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(help_text="Author's biography", null=True, blank=True)
    specializations = models.ManyToManyField(
        learning.models.Category,
        help_text="Specializations of author",
        related_name='author', null=True, blank=True)

    def __str__(self):
        return self.user.full_name

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'


class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField('learning.Course', related_name='user_courses')
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    score = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rank = models.IntegerField()

    class Meta:
        verbose_name = 'User course'
        verbose_name_plural = 'User courses'

    def __str__(self):
        return f"{self.user.full_name} - {self.courses}"


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
    last_interaction = models.DateField(null=True, blank=True)
    current_streak = models.IntegerField(default=0)
    type = models.IntegerField(choices=STREAK_TYPE_CHOICES)
    highest_streak = models.IntegerField('highest streak', default=0)

    class Meta:
        verbose_name = 'Streak'
        verbose_name_plural = 'Streaks'

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

    question = models.ManyToManyField(learning.models.BaseQuestion, related_name='question_for_user_response')

    text_answer = ArrayField(
        models.CharField(max_length=255),
        null=True,
        blank=True)

    choice_answers = models.ManyToManyField(
        learning.models.Choice,
        related_name='correct_choices_for_user_response',
        help_text="Correct choice options",
    )

    submitted_at = models.DateTimeField('submitted at', auto_now_add=True)

    class Meta:
        verbose_name = 'User response'
        verbose_name_plural = 'User responses'

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

    class Meta:
        verbose_name = 'Staff member'
        verbose_name_plural = 'Staff members'

    def __str__(self):
        return f"{self.user.full_name} - {self.get_role_type_display()}"
