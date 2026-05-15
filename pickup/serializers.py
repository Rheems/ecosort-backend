from rest_framework import serializers
from .models import PickupRequest, ConfirmationCode

class PickupRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupRequest
        fields = ['id', 'waste_type', 'weight_kg', 'points_credited', 'status', 'created_at']
        read_only_fields = ['points_credited', 'status']

class ConfirmationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfirmationCode
        fields = ['code', 'expires_at', 'is_used']