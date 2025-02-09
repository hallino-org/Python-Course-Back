# # learning/admin.py
# from django.contrib import admin
# from django import forms
# from django.urls import reverse
# from django.utils.html import format_html
#
# from . import models as learning_models
#
#
# @admin.register(learning_models.Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['title', 'course_count']
#     search_fields = ['title', 'description']
#
#     def course_count(self, obj):
#         return obj.courses.count()
#
#     course_count.short_description = 'Number of Courses'
#
#
# class ChapterInline(admin.TabularInline):
#     model = learning_models.Chapter
#     extra = 1
#     show_change_link = True
#     fields = ['title', 'order', 'estimated_time', 'is_active']
#
#
# @admin.register(learning_models.Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = [
#         'title', 'slug', 'get_level_display',
#         'get_language_display', 'price',
#         'is_published', 'is_active', 'rating'
#     ]
#     list_filter = ['level', 'language', 'is_published', 'is_active', 'categories']
#     search_fields = ['title', 'slug', 'description']
#     prepopulated_fields = {'slug': ('title',)}  # Auto-populate slug from title
#     readonly_fields = ['created_at', 'updated_at', 'rating']
#
#     fieldsets = (
#         ('Basic Information', {
#             'fields': ('title', 'slug', 'description', 'logo', 'video_url')
#         }),
#         ('Course Details', {
#             'fields': ('level', 'language', 'duration', 'price')
#         }),
#         ('Categories and Authors', {
#             'fields': ('categories', 'authors', 'requirements')
#         }),
#         ('Schedule', {
#             'fields': ('start_date', 'end_date')
#         }),
#         ('Status', {
#             'fields': ('is_published', 'is_active', 'rating')
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def get_level_display(self, obj):
#         return obj.get_level_display()
#
#     get_level_display.short_description = 'Level'
#
#     def get_language_display(self, obj):
#         return obj.get_language_display()
#
#     get_language_display.short_description = 'Language'
#
#     @staticmethod
#     def view_on_site(obj):
#         return obj.get_absolute_url()
#
#
# class LessonInline(admin.TabularInline):
#     model = learning_models.Lesson
#     extra = 1
#     show_change_link = True
#     fields = ['title', 'order', 'duration', 'lesson_type', 'is_active']
#
#
# @admin.register(learning_models.Chapter)
# class ChapterAdmin(admin.ModelAdmin):
#     list_display = [
#         'title', 'course_link', 'order',
#         'estimated_time', 'is_active', 'lesson_count'
#     ]
#     list_filter = ['is_active', 'course__title']
#     search_fields = ['title', 'description', 'course__title']
#     inlines = [LessonInline]
#     ordering = ['course', 'order']
#
#     def course_link(self, obj):
#         url = reverse('admin:learning_course_change', args=[obj.course.id])
#         return format_html('<a href="{}">{}</a>', url, obj.course.title)
#
#     course_link.short_description = 'Course'
#
#     def lesson_count(self, obj):
#         return obj.lessons.count()
#
#     lesson_count.short_description = 'Number of Lessons'
#
#
# class SlideInline(admin.StackedInline):
#     model = learning_models.Slide
#     extra = 1
#     show_change_link = True
#     fields = [
#         'title', 'content', 'type', 'order',
#         'time_limit', 'is_active', 'is_required',
#         'question', 'total_marks'
#     ]
#
#
# @admin.register(learning_models.Lesson)
# class LessonAdmin(admin.ModelAdmin):
#     list_display = [
#         'title', 'chapter_link', 'order',
#         'duration', 'lesson_type', 'is_active',
#         'slide_count'
#     ]
#     list_filter = ['is_active', 'lesson_type', 'chapter__course__title']
#     search_fields = ['title', 'description', 'chapter__title']
#     inlines = [SlideInline]
#     ordering = ['chapter', 'order']
#
#     def chapter_link(self, obj):
#         url = reverse('admin:learning_chapter_change', args=[obj.chapter.id])
#         return format_html('<a href="{}">{}</a>', url, obj.chapter.title)
#
#     chapter_link.short_description = 'Chapter'
#
#     def slide_count(self, obj):
#         return obj.slides.count()
#
#     slide_count.short_description = 'Number of Slides'
#
#
# class ChoiceInline(admin.TabularInline):
#     model = learning_models.Choice
#     extra = 2
#     fields = ['text', 'type', 'order', 'image', 'alt_text', 'hidden']
#
#
# @admin.register(learning_models.BaseQuestion)
# class BaseQuestionAdmin(admin.ModelAdmin):
#     list_display = [
#         'title', 'question_type', 'created_at',
#         'editor_link'
#     ]
#     list_filter = ['question_type', 'editor']
#     search_fields = ['title', 'description']
#     readonly_fields = ['created_at', 'updated_at']
#
#     def editor_link(self, obj):
#         if obj.editor:
#             url = reverse('admin:users_staff_change', args=[obj.editor.id])
#             return format_html('<a href="{}">{}</a>', url, obj.editor)
#         return '-'
#
#     editor_link.short_description = 'Editor'
#
#
# @admin.register(learning_models.ChoiceQuestion)
# class ChoiceQuestionAdmin(admin.ModelAdmin):
#     list_display = [
#         'title', 'is_multiselect', 'created_at',
#         'editor_link', 'choice_count'
#     ]
#     list_filter = ['is_multiselect', 'editor']
#     search_fields = ['title', 'description']
#     # filter_horizontal = ['correct_choices']
#     inlines = [ChoiceInline]
#
#     def editor_link(self, obj):
#         if obj.editor:
#             url = reverse('admin:users_staff_change', args=[obj.editor.id])
#             return format_html('<a href="{}">{}</a>', url, obj.editor)
#         return '-'
#
#     editor_link.short_description = 'Editor'
#
#     def choice_count(self, obj):
#         return obj.choices.count()
#
#     choice_count.short_description = 'Number of Choices'
#
#
# class TextQuestionForm(forms.ModelForm):
#     # Convert ArrayField to textarea for better editing
#     choices_text = forms.CharField(
#         widget=forms.Textarea(attrs={'rows': 3}),
#         required=False,
#         help_text="Enter one choice per line"
#     )
#
#     correct_answer_text = forms.CharField(
#         widget=forms.Textarea(attrs={'rows': 3}),
#         help_text="Enter one correct answer per line"
#     )
#
#     class Meta:
#         model = learning_models.TextQuestion
#         fields = '__all__'
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         instance = kwargs.get('instance')
#         if instance:
#             self.fields['choices_text'].initial = '\n'.join(instance.choices or [])
#             self.fields['correct_answer_text'].initial = '\n'.join(instance.correct_answer or [])
#
#     def clean_choices_text(self):
#         text = self.cleaned_data['choices_text']
#         return [choice.strip() for choice in text.split('\n') if choice.strip()]
#
#     def clean_correct_answer_text(self):
#         text = self.cleaned_data['correct_answer_text']
#         return [answer.strip() for answer in text.split('\n') if answer.strip()]
#
#     def clean(self):
#         cleaned_data = super().clean()
#         choices = cleaned_data.get('choices_text', [])
#         correct_answers = cleaned_data.get('correct_answer_text', [])
#         selectable = cleaned_data.get('selectable', False)
#
#         if selectable and not choices:
#             raise forms.ValidationError(
#                 "Choices must be provided when question is selectable"
#             )
#
#         if selectable:
#             invalid_answers = [ans for ans in correct_answers if ans not in choices]
#             if invalid_answers:
#                 raise forms.ValidationError(
#                     f"Correct answers {invalid_answers} are not in the choices list"
#                 )
#
#         return cleaned_data
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.choices = self.cleaned_data['choices_text']
#         instance.correct_answer = self.cleaned_data['correct_answer_text']
#         if commit:
#             instance.save()
#         return instance
#
#
# @admin.register(learning_models.TextQuestion)
# class TextQuestionAdmin(admin.ModelAdmin):
#     form = TextQuestionForm
#
#     list_display = [
#         'title',
#         'question_type',
#         'selectable',
#         'choices_count',
#         'correct_answers_count',
#         'created_at'
#     ]
#
#     list_filter = ['selectable', 'question_type']
#     search_fields = ['title', 'description']
#     readonly_fields = ['created_at', 'updated_at']
#
#     fieldsets = (
#         ('Question Information', {
#             'fields': ('title', 'description', 'question_type')
#         }),
#         ('Answer Configuration', {
#             'fields': ('selectable', 'choices_text', 'correct_answer_text')
#         }),
#         ('Media', {
#             'fields': ('image', 'video_url'),
#             'classes': ('collapse',)
#         }),
#         ('Additional Information', {
#             'fields': ('answer_description', 'editor'),
#             'classes': ('collapse',)
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def choices_count(self, obj):
#         return len(obj.choices) if obj.choices else 0
#
#     choices_count.short_description = 'Number of Choices'
#
#     def correct_answers_count(self, obj):
#         return len(obj.correct_answer) if obj.correct_answer else 0
#
#     correct_answers_count.short_description = 'Number of Correct Answers'
#
#
# @admin.register(learning_models.Slide)
# class SlideAdmin(admin.ModelAdmin):
#     list_display = [
#         'title', 'lesson_link', 'type',
#         'is_active', 'is_required', 'order'
#     ]
#     list_filter = ['type', 'is_active', 'is_required']
#     search_fields = ['title', 'content']
#     readonly_fields = ['created_at', 'updated_at', 'comments_count']
#     fieldsets = (
#         ('Basic Information', {
#             'fields': ('lesson', 'title', 'content', 'type', 'order')
#         }),
#         ('Media', {
#             'fields': ('image', 'video_url', 'alt_text')
#         }),
#         ('Quiz Settings', {
#             'fields': ('question', 'total_marks', 'time_limit', 'hints')
#         }),
#         ('Status', {
#             'fields': ('is_active', 'is_required', 'comments_count')
#         }),
#         ('Editor Information', {
#             'fields': ('editor', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def lesson_link(self, obj):
#         url = reverse('admin:learning_lesson_change', args=[obj.lesson.id])
#         return format_html('<a href="{}">{}</a>', url, obj.lesson.title)
#
#     lesson_link.short_description = 'Lesson'
#
#
# # Register the Choice model with a basic admin interface
# @admin.register(learning_models.Choice)
# class ChoiceAdmin(admin.ModelAdmin):
#     list_display = ['text', 'question', 'type', 'order', 'hidden']
#     list_filter = ['type', 'hidden', 'question']
#     search_fields = ['text', 'alt_text']
#     ordering = ['question', 'order']
#
#
# @admin.register(learning_models.Editor)
# class EditorAdmin(admin.ModelAdmin):
#     list_display = [
#         'get_lang_display',
#         'truncated_code',
#         'executable',
#         'created_at',
#         'updated_at'
#     ]
#     list_filter = ['lang', 'executable']
#     search_fields = ['initial_code']
#     readonly_fields = ['created_at', 'updated_at']
#
#     fieldsets = (
#         ('Editor Configuration', {
#             'fields': ('lang', 'executable')
#         }),
#         ('Code', {
#             'fields': ('initial_code',),
#             'classes': ('wide',)
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def truncated_code(self, obj):
#         """Display first 50 characters of code in admin list view"""
#         if len(obj.initial_code) > 50:
#             return f"{obj.initial_code[:50]}..."
#         return obj.initial_code
#
#     truncated_code.short_description = 'Initial Code'
# from django.contrib import admin
#
# from .models import (
#     Category, Course, Chapter, Lesson, Editor,
#     BaseQuestion, Choice, ChoiceQuestion, TextQuestion, Slide
# )
#
#
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('title', 'description')
#     search_fields = ('title',)
#
#
# class ChapterInline(admin.TabularInline):
#     model = Chapter
#     extra = 1
#     fields = ('title', 'order', 'is_active', 'estimated_time')
#
#
# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('title', 'display_price', 'level', 'language', 'rating', 'is_published', 'is_active')
#     list_filter = ('level', 'language', 'is_published', 'is_active', 'categories')
#     search_fields = ('title', 'description')
#     prepopulated_fields = {'slug': ('title',)}
#     filter_horizontal = ('authors', 'categories', 'requirements')
#     inlines = [ChapterInline]
#     date_hierarchy = 'created_at'
#
#     def display_price(self, obj):
#         return f"{obj.price:,} Rials"
#
#     display_price.short_description = 'Price'
#
#
# class LessonInline(admin.TabularInline):
#     model = Lesson
#     extra = 1
#     fields = ('title', 'order', 'duration', 'is_required', 'is_active', 'lesson_type')
#
#
# @admin.register(Chapter)
# class ChapterAdmin(admin.ModelAdmin):
#     list_display = ('title', 'course', 'order', 'estimated_time', 'is_active')
#     list_filter = ('is_active', 'course')
#     search_fields = ('title', 'course__title')
#     inlines = [LessonInline]
#     ordering = ('course', 'order')
#
#
# class SlideInline(admin.TabularInline):
#     model = Slide
#     extra = 1
#     fields = ('title', 'order', 'type', 'is_required', 'is_active')
#
#
# @admin.register(Lesson)
# class LessonAdmin(admin.ModelAdmin):
#     list_display = ('title', 'chapter', 'order', 'duration', 'score', 'lesson_type', 'is_active')
#     list_filter = ('lesson_type', 'is_active', 'is_required')
#     search_fields = ('title', 'chapter__title', 'chapter__course__title')
#     inlines = [SlideInline]
#     ordering = ('chapter', 'order')
#
#
# @admin.register(Editor)
# class EditorAdmin(admin.ModelAdmin):
#     list_display = ('lang', 'executable', 'created_at', 'display_initial_code')
#     list_filter = ('lang', 'executable')
#     search_fields = ('initial_code',)
#
#     def display_initial_code(self, obj):
#         return obj.initial_code[:50] + '...' if len(obj.initial_code) > 50 else obj.initial_code
#
#     display_initial_code.short_description = 'Initial Code'
#
#
# class ChoiceInline(admin.TabularInline):
#     model = Choice
#     extra = 1
#     fields = ('text', 'order', 'type', 'hidden')
#
#
# @admin.register(BaseQuestion)
# class BaseQuestionAdmin(admin.ModelAdmin):
#     list_display = ('title', 'question_type', 'created_at')
#     list_filter = ('question_type',)
#     search_fields = ('title', 'description')
#     inlines = [ChoiceInline]
#     readonly_fields = ('created_at', 'updated_at')
#
#
# @admin.register(Choice)
# class ChoiceAdmin(admin.ModelAdmin):
#     list_display = ('text', 'question', 'order', 'type', 'hidden')
#     list_filter = ('type', 'hidden')
#     search_fields = ('text', 'question__title')
#     ordering = ('question', 'order')
#
#
# @admin.register(ChoiceQuestion)
# class ChoiceQuestionAdmin(admin.ModelAdmin):
#     list_display = ('title', 'is_multiselect', 'question_type', 'display_choices', 'display_correct_answer')
#     list_filter = ('is_multiselect', 'question_type')
#     search_fields = ('title', 'description')
#     filter_horizontal = ('choices',)
#     raw_id_fields = ('correct_answer',)
#
#     def display_choices(self, obj):
#         return ", ".join([choice.text for choice in obj.choices.all()[:3]])
#
#     display_choices.short_description = 'Choices'
#
#     def display_correct_answer(self, obj):
#         return obj.correct_answer.text if obj.correct_answer else '-'
#
#     display_correct_answer.short_description = 'Correct Answer'
#
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'description', 'question_type')
#         }),
#         ('Choices', {
#             'fields': ('choices', 'is_multiselect', 'correct_answer')
#         }),
#         ('Additional Info', {
#             'fields': ('image', 'video_url', 'answer_description', 'editor')
#         }),
#     )
#
#
# @admin.register(TextQuestion)
# class TextQuestionAdmin(admin.ModelAdmin):
#     list_display = ('title', 'selectable', 'question_type', 'display_choices', 'display_correct_answers')
#     list_filter = ('selectable', 'question_type')
#     search_fields = ('title', 'description')
#     filter_horizontal = ('choices', 'correct_answers')
#
#     def display_choices(self, obj):
#         return ", ".join([choice.text for choice in obj.choices.all()[:3]])
#
#     display_choices.short_description = 'Choices'
#
#     def display_correct_answers(self, obj):
#         return ", ".join([answer.text for answer in obj.correct_answers.all()[:3]])
#
#     display_correct_answers.short_description = 'Correct Answers'
#
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'description', 'question_type')
#         }),
#         ('Choices and Answers', {
#             'fields': ('choices', 'selectable', 'correct_answers')
#         }),
#         ('Additional Info', {
#             'fields': ('image', 'video_url', 'answer_description', 'editor')
#         }),
#     )
#
#
# @admin.register(Slide)
# class SlideAdmin(admin.ModelAdmin):
#     list_display = ('title', 'lesson', 'type', 'is_active', 'is_required', 'order')
#     list_filter = ('type', 'is_active', 'is_required')
#     search_fields = ('title', 'content', 'lesson__title')
#     raw_id_fields = ('question', 'editor')
#     readonly_fields = ('comments_count', 'created_at', 'updated_at')
#     fieldsets = (
#         (None, {
#             'fields': ('lesson', 'title', 'content', 'order', 'type')
#         }),
#         ('Status', {
#             'fields': ('is_active', 'is_required')
#         }),
#         ('Media', {
#             'fields': ('image', 'video_url', 'alt_text')
#         }),
#         ('Quiz Settings', {
#             'fields': ('total_marks', 'time_limit', 'hints', 'question')
#         }),
#         ('Meta', {
#             'fields': ('editor', 'comments_count', 'created_at', 'updated_at')
#         })
#     )
# learning/admin.py
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Category, Course, Chapter, Lesson,
    Editor, BaseQuestion, Choice, Slide
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'courses_count']
    search_fields = ['title', 'description']
    list_per_page = 20

    def courses_count(self, obj):
        return obj.courses.count()

    courses_count.short_description = 'Courses'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            courses_count=Count('courses', distinct=True)
        )


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    show_change_link = True
    fields = ['title', 'order', 'is_active']
    ordering = ['order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

    list_display = [
        'title', 'level', 'language', 'price',
        'is_published', 'is_active', 'rating',
        'chapters_count', 'view_authors'
    ]
    list_filter = [
        'level', 'language', 'is_published',
        'is_active', 'categories'
    ]
    search_fields = ['title', 'slug', 'description', 'authors__user__email']
    filter_horizontal = ['categories', 'authors', 'requirements']
    readonly_fields = ['created_at', 'updated_at', 'rating']
    list_editable = ['is_published', 'is_active']
    list_per_page = 20
    inlines = [ChapterInline]
    save_on_top = True

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'level', 'language')
        }),
        ('Course Details', {
            'fields': ('duration', 'price', 'logo', 'video_url')
        }),
        ('Categories and Authors', {
            'fields': ('categories', 'authors', 'requirements')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_published', 'is_active', 'rating')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def view_authors(self, obj):
        authors = obj.authors.all()
        return format_html(
            '<br>'.join(
                '<a href="{}">{}</a>'.format(
                    reverse('admin:users_author_change', args=[author.pk]),
                    author.user.full_name
                ) for author in authors
            )
        )

    view_authors.short_description = 'Authors'

    def chapters_count(self, obj):
        return obj.chapters.count()

    chapters_count.short_description = 'Chapters'

    actions = ['publish_courses', 'unpublish_courses']

    def publish_courses(self, request, queryset):
        queryset.update(is_published=True)

    publish_courses.short_description = 'Publish selected courses'

    def unpublish_courses(self, request, queryset):
        queryset.update(is_published=False)

    unpublish_courses.short_description = 'Unpublish selected courses'


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    show_change_link = True
    fields = ['title', 'order', 'duration', 'is_active']
    ordering = ['order']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'course', 'order',
        'is_active', 'lessons_count', 'estimated_time'
    ]
    list_filter = ['is_active', 'course']
    search_fields = ['title', 'description', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['order', 'is_active']
    inlines = [LessonInline]
    list_per_page = 20

    def lessons_count(self, obj):
        return obj.lessons.count()

    lessons_count.short_description = 'Lessons'


class SlideInline(admin.StackedInline):
    model = Slide
    extra = 1
    show_change_link = True
    fields = [
        'title', 'content', 'type',
        'order', 'is_active', 'is_required'
    ]
    ordering = ['order']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'chapter', 'lesson_type',
        'duration', 'is_required', 'is_active',
        'slides_count'
    ]
    list_filter = ['lesson_type', 'is_required', 'is_active', 'chapter']
    search_fields = ['title', 'description', 'chapter__title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_required', 'is_active']
    inlines = [SlideInline]
    list_per_page = 20

    def slides_count(self, obj):
        return obj.slides.count()

    slides_count.short_description = 'Slides'


@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    list_display = ['lang', 'executable', 'created_at']
    list_filter = ['lang', 'executable']
    search_fields = ['initial_code']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1
    fields = ['text', 'type', 'order', 'is_correct', 'hidden']
    ordering = ['order']


@admin.register(BaseQuestion)
class BaseQuestionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'question_type',
        'is_text_input', 'has_image',
        'has_video', 'choices_count'
    ]
    list_filter = ['question_type', 'is_text_input']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ChoiceInline]
    list_per_page = 20

    def has_image(self, obj):
        return bool(obj.image)

    has_image.boolean = True
    has_image.short_description = 'Has Image'

    def has_video(self, obj):
        return bool(obj.video_url)

    has_video.boolean = True
    has_video.short_description = 'Has Video'

    def choices_count(self, obj):
        return obj.choices.count()

    choices_count.short_description = 'Choices'


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = [
        'text', 'question', 'type',
        'order', 'is_correct', 'hidden'
    ]
    list_filter = ['type', 'is_correct', 'hidden']
    search_fields = ['text', 'question__title']
    list_editable = ['order', 'is_correct', 'hidden']
    list_per_page = 20


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'lesson', 'type',
        'is_active', 'is_required',
        'has_question', 'comments_count'
    ]
    list_filter = ['type', 'is_active', 'is_required']
    search_fields = ['title', 'content', 'lesson__title']
    readonly_fields = ['created_at', 'updated_at', 'comments_count']
    list_editable = ['is_active', 'is_required']
    list_per_page = 20

    def has_question(self, obj):
        return bool(obj.question)

    has_question.boolean = True
    has_question.short_description = 'Has Question'
