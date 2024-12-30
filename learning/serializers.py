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
