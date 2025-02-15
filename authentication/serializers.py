from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.serializers import UserBaseSerializer

User = get_user_model()


class RegisterSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ['password']

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match."
            })

        try:
            password_validation.validate_password(data.get('password'))
        except ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
