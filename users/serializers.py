from rest_framework import serializers
from .models import User, UserProfile, OnboardingSession

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True)
    location = serializers.CharField(write_only=True, required=False)
    language = serializers.CharField(write_only=True, required=False)
    waste_type = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'email',
            'phone_number',
            'password',
            'user_type',
            'full_name',
            'location',
            'language',
            'waste_type',
        ]

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        location = validated_data.pop('location', None)
        language = validated_data.pop('language', 'english')
        waste_type = validated_data.pop('waste_type', None)

        user = User.objects.create_user(
            username=validated_data.get('email'),
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number'),
            user_type=validated_data['user_type'],
        )

        UserProfile.objects.create(
            user=user,
            full_name=full_name,
            location=location,
            language_preference=language,
            waste_type=waste_type,
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'full_name',
            'location',
            'language_preference',
            'channel',
            'waste_type',
        ]


class OnboardingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingSession
        fields = [
            'current_step',
            'step_1_completed',
            'step_2_completed',
            'step_3_completed',
            'step_4_completed',
            'step_5_completed',
            'is_completed',
            'started_at',
            'completed_at',
        ]