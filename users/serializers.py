# users/serializers.py
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers

from learning.serializers import CategorySerializer, CourseSerializer
from .models import User, Author, UserCourse, Streak, UserResponse, Staff


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'firstname', 'lastname', 'gender',
            'phone_number', 'birth_date', 'type', 'level',
            'is_active', 'is_confirmed', 'password',
            'confirm_password', 'created_at', 'updated_at',
            'expire_date', 'full_name'
        ]
        read_only_fields = ['is_active', 'is_confirmed', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class AuthorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    specializations = CategorySerializer()
    active_courses = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id', 'user', 'bio', 'specializations',
            'total_courses', 'active_courses'
        ]

    def get_active_courses(self, obj):
        active_courses = obj.courses.filter(is_active=True)
        return CourseSerializer(active_courses, many=True).data


class UserCourseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = UserCourse
        fields = [
            'id', 'user', 'course', 'progress',
            'score', 'rank'
        ]

    def validate_progress(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError("Progress must be between 0 and 100")
        return value


class StreakSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Streak
        fields = [
            'id', 'user', 'last_interaction', 'current_streak',
            'type', 'highest_streak', 'days_remaining'
        ]

    def get_days_remaining(self, obj):
        if not obj.last_interaction:
            return 0
        days_passed = (timezone.now().date() - obj.last_interaction).days
        return max(0, obj.type - days_passed)


class UserResponseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserResponse
        fields = [
            'id', 'user', 'question', 'text_answer',
            'choice_answers', 'submitted_at'
        ]
        read_only_fields = ['submitted_at']


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Staff
        fields = ['id', 'user', 'role_type']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        staff = Staff.objects.create(user=user, **validated_data)
        return staff


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")
        return data
