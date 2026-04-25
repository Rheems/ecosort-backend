from rest_framework import serializers
from .models import User, UserProfile, OnboardingSession

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'phone_number', 'user_type']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number'),
            user_type=validated_data['user_type'],
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'location', 'language_preference', 'channel']


class OnboardingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingSession
        fields = ['current_step', 'is_completed', 'started_at', 'completed_at']