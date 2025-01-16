from django.utils.text import slugify
from rest_framework import serializers

from .models import (
    Category, Course, Chapter, Lesson, Editor,
    BaseQuestion, Choice, Slide
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'description']


class EditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editor
        fields = [
            'id', 'initial_code', 'lang', 'executable',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = [
            'id', 'question', 'text', 'alt_text', 'image',
            'order', 'hidden', 'type', 'is_correct'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        if data.get('type') == 2 and not data.get('image'):
            raise serializers.ValidationError(
                "Picture choices must have an image"
            )
        if data.get('type') == 1 and not data.get('text'):
            raise serializers.ValidationError(
                "Text choices must have text"
            )
        return data


class BaseQuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    correct_choices = serializers.SerializerMethodField()

    class Meta:
        model = BaseQuestion
        fields = [
            'id', 'title', 'description', 'question_type',
            'image', 'video_url', 'answer_description',
            'editor', 'is_text_input', 'choices',
            'correct_choices', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_correct_choices(self, obj):
        return ChoiceSerializer(
            obj.choices.filter(is_correct=True),
            many=True
        ).data

    def validate(self, data):
        if self.instance:
            choices = self.instance.choices.all()
            if data.get('question_type') in [1, 2]:
                if not choices.exists():
                    raise serializers.ValidationError(
                        "Choice questions must have at least one choice"
                    )
                if data.get('question_type') == 1:
                    correct_count = choices.filter(is_correct=True).count()
                    if correct_count != 1:
                        raise serializers.ValidationError(
                            "Single choice questions must have exactly one correct answer"
                        )
        return data


class SlideSerializer(serializers.ModelSerializer):
    question_detail = BaseQuestionSerializer(source='question', read_only=True)

    class Meta:
        model = Slide
        fields = [
            'id', 'lesson', 'title', 'content', 'total_marks',
            'type', 'time_limit', 'is_active', 'is_required',
            'hints', 'alt_text', 'image', 'video_url',
            'question', 'question_detail',
            'editor', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        if data.get('type') == 2:
            if not data.get('question'):
                raise serializers.ValidationError(
                    "Quiz slides must have an associated question"
                )
        return data


class LessonSerializer(serializers.ModelSerializer):
    slides = SlideSerializer(many=True, read_only=True)

    # active_slides = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'chapter', 'title', 'description', 'order',
            'duration', 'is_required', 'is_active', 'score',
            'lesson_type', 'slides',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    # def get_active_slides(self, obj):
    #     return SlideSerializer(
    #         obj.get_active_slides(),
    #         many=True
    #     ).data


class ChapterSerializer(serializers.ModelSerializer):
    # lessons = LessonSerializer(many=True, read_only=True)
    # active_lessons = serializers.SerializerMethodField()
    active_lessons_ids = serializers.PrimaryKeyRelatedField(many=True, source='lessons', read_only=True)

    class Meta:
        model = Chapter
        fields = [
            'id', 'course', 'title', 'description', 'order',
            'image', 'estimated_time', 'is_active',
            'active_lessons_ids', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    # def get_active_lessons(self, obj):
    #     return LessonSerializer(
    #         obj.get_active_lessons(),
    #         many=True
    #     ).data

    def get_active_lessons_ids(self, obj):
        active_lessons = obj.get_active_lessons()
        return [lesson.id for lesson in active_lessons]


class CourseSerializer(serializers.ModelSerializer):
    # chapters = ChapterSerializer(many=True, read_only=True)
    active_chapters = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)
    requirements = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Course.objects.all(),
        required=False
    )

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'authors',
            'categories', 'duration', 'level', 'price',
            'start_date', 'end_date', 'is_published',
            'is_active', 'logo', 'video_url', 'requirements',
            'active_chapters', 'language', 'rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'rating', 'slug'
        ]

    def get_active_chapters(self, obj):
        return ChapterSerializer(
            obj.get_active_chapters(),
            many=True
        ).data

    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError(
                    "End date must be after start date"
                )

        if 'requirements' in data:
            course_id = self.instance.id if self.instance else None
            for req in data['requirements']:
                if req.id == course_id:
                    raise serializers.ValidationError(
                        "A course cannot be its own requirement"
                    )
                if course_id in [r.id for r in req.requirements.all()]:
                    raise serializers.ValidationError(
                        "Circular dependency in course requirements"
                    )

        return data

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['title'])

        categories = validated_data.pop('categories', [])
        authors = validated_data.pop('authors', [])
        requirements = validated_data.pop('requirements', [])

        course = super().create(validated_data)

        course.categories.set(categories)
        course.authors.set(authors)
        course.requirements.set(requirements)

        return course
