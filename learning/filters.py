from django_filters import rest_framework as filters

from .learning_constants import LearningConstants
from .models import Course, Chapter, Lesson, BaseQuestion, Slide


class CourseFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    language = filters.ChoiceFilter(choices=Course.LANGUAGE_CHOICES)
    level = filters.ChoiceFilter(choices=LearningConstants.LEVEL_CHOICES)
    category = filters.CharFilter(field_name='categories__title')
    author = filters.CharFilter(field_name='authors__username')

    class Meta:
        model = Course
        fields = ['is_published', 'is_active', 'language', 'level']


class ChapterFilter(filters.FilterSet):
    course = filters.NumberFilter(field_name='course__id')

    class Meta:
        model = Chapter
        fields = ['course', 'is_active']


class LessonFilter(filters.FilterSet):
    chapter = filters.NumberFilter(field_name='chapter__id')
    course = filters.NumberFilter(field_name='chapter__course__id')
    lesson_type = filters.ChoiceFilter(choices=LearningConstants.LESSON_TYPE_CHOICES)

    class Meta:
        model = Lesson
        fields = ['chapter', 'is_active', 'is_required', 'lesson_type']


class QuestionFilter(filters.FilterSet):
    question_type = filters.ChoiceFilter(choices=LearningConstants.QUESTION_TYPE_CHOICES)

    class Meta:
        model = BaseQuestion
        fields = ['question_type', 'is_text_input']


class SlideFilter(filters.FilterSet):
    lesson = filters.NumberFilter(field_name='lesson__id')
    chapter = filters.NumberFilter(field_name='lesson__chapter__id')
    course = filters.NumberFilter(field_name='lesson__chapter__course__id')
    slide_type = filters.ChoiceFilter(field_name='type', choices=LearningConstants.SLIDE_TYPE_CHOICES)

    class Meta:
        model = Slide
        fields = ['lesson', 'is_active', 'is_required', 'type']