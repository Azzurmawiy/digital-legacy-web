# apps/authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
import pyotp
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import random

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'password', 'phone', 'first_name', 'last_name']
        extra_kwargs = {
            'phone': {'required': False, 'allow_null': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.is_active = False
        user.is_email_verified = False
        user.save()
        return user

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    totp_token = serializers.CharField(required=False, allow_blank=True)

class MFASetupSerializer(serializers.Serializer):
    pass  # Just for triggering MFA setup

class MFASetupResponseSerializer(serializers.Serializer):
    secret = serializers.CharField()
    provisioning_uri = serializers.CharField()