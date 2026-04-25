from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import User, UserProfile, OnboardingSession, RewardNotificationQueue
from .serializers import RegisterSerializer, UserProfileSerializer, OnboardingSessionSerializer

# REGISTER
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        OnboardingSession.objects.create(user=user)
        return Response({
            'message': 'Registration successful!',
            'user_id': user.id,
            'user_type': user.user_type,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET & UPDATE PROFILE
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({'message': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# COMPLETE ONBOARDING
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_onboarding(request):
    try:
        session = OnboardingSession.objects.get(user=request.user)
    except OnboardingSession.DoesNotExist:
        return Response({'message': 'Onboarding session not found'}, status=status.HTTP_404_NOT_FOUND)

    if session.is_completed:
        return Response({'message': 'Onboarding already completed!'})

    session.is_completed = True
    session.completed_at = timezone.now()
    session.save()

    RewardNotificationQueue.objects.create(
        user=request.user,
        notification_type='first_reward',
        status='pending',
    )

    return Response({
        'message': 'Onboarding complete! First reward notification queued.',
    }, status=status.HTTP_200_OK)


# ONBOARDING STATUS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def onboarding_status(request):
    try:
        session = OnboardingSession.objects.get(user=request.user)
        serializer = OnboardingSessionSerializer(session)
        return Response(serializer.data)
    except OnboardingSession.DoesNotExist:
        return Response({'message': 'No onboarding session found'}, status=status.HTTP_404_NOT_FOUND)


# Create your views here.
