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
