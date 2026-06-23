from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'full_name', 'student_id',
            'course', 'year_of_study', 'role', 'is_verified',
            'profile_picture', 'date_joined',
        ]
        read_only_fields = ['id', 'role', 'is_verified', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'phone_number', 'email', 'full_name', 'student_id',
            'course', 'year_of_study', 'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_verified = False
        user.role = 'student'
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
