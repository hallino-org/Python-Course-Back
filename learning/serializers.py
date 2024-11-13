from rest_framework import serializers

from .models import Course, Chapter, Lesson, Slide, BaseQuestion, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'alt_text', 'image', 'order', 'type']


class BaseQuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = BaseQuestion
        fields = [
            'id', 'title', 'description', 'question_type',
            'image', 'video_url', 'answer_description', 'choices'
        ]


class SlideSerializer(serializers.ModelSerializer):
    question = BaseQuestionSerializer(read_only=True)

    class Meta:
        model = Slide
        fields = [
            'id', 'title', 'content', 'type', 'time_limit',
            'is_active', 'is_required', 'hints', 'image',
            'video_url', 'total_marks', 'question', 'order'
        ]


class LessonSerializer(serializers.ModelSerializer):
    slides = SlideSerializer(many=True, read_only=True, source='get_active_slides')

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'order', 'duration',
            'is_required', 'is_active', 'score', 'lesson_type',
            'slides'
        ]


class ChapterSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True, source='get_active_lessons')

    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'description', 'order',
            'image', 'estimated_time', 'is_active', 'lessons'
        ]


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'level', 'price', 'authors',
            'duration', 'rating', 'language', 'logo',
            'is_published', 'is_active', 'start_date', 'end_date'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True, source='get_active_chapters')
    authors = serializers.StringRelatedField(many=True)
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'authors', 'categories',
            'duration', 'level', 'price', 'start_date', 'end_date',
            'is_published', 'is_active', 'logo', 'video_url',
            'language', 'rating', 'chapters'
        ]
