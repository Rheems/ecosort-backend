from django.db import models
from .models import User, UserProfile, OnboardingSession, RewardNotificationQueue, OTPVerification
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from .serializers import RegisterSerializer, UserProfileSerializer, OnboardingSessionSerializer
import random


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


# LOGIN
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')

    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid phone number or password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.check_password(password):
        return Response(
            {'error': 'Invalid phone number or password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'message': 'Login successful!',
        'token': token.key,
        'user_id': user.id,
        'user_type': user.user_type,
    }, status=status.HTTP_200_OK)


# REQUEST OTP
@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    phone_number = request.data.get('phone_number')

    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return Response(
            {'error': 'No account found with this phone number'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Save OTP — store phone_number directly (matches OTPVerification model)
    OTPVerification.objects.create(
        phone_number=phone_number,
        otp=otp
    )

    return Response({
        'message': 'OTP generated successfully!',
        'otp': otp,
        'note': 'In production this OTP will be sent via SMS'
    }, status=status.HTTP_200_OK)


# VERIFY OTP
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    phone_number = request.data.get('phone_number')
    otp = request.data.get('otp')

    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return Response(
            {'error': 'No account found with this phone number'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Look up OTP by phone_number (matches how we store it)
    try:
        otp_record = OTPVerification.objects.filter(
            phone_number=phone_number,
            is_used=False
        ).latest('created_at')
    except OTPVerification.DoesNotExist:
        return Response(
            {'error': 'No OTP found. Please request a new one'},
            status=status.HTTP_404_NOT_FOUND
        )

    if otp_record.otp != otp:
        return Response(
            {'error': 'Invalid OTP'},
            status=status.HTTP_400_BAD_REQUEST
        )

    otp_record.is_used = True
    otp_record.save()

    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'message': 'OTP verified! Login successful!',
        'token': token.key,
        'user_id': user.id,
        'user_type': user.user_type,
    }, status=status.HTTP_200_OK)


# GET & UPDATE PROFILE
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response(
            {'message': 'Profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET POINTS BALANCE
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_points(request):
    from pickup.models import PickupRequest
    total_points = PickupRequest.objects.filter(
        user=request.user,
        status='completed'
    ).aggregate(total=Sum('points_credited'))['total'] or 0

    return Response({
        'user_id': request.user.id,
        'total_points': total_points,
        'message': f'You have {total_points} points'
    }, status=status.HTTP_200_OK)


# COMPLETE ONBOARDING
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_onboarding(request):
    try:
        session = OnboardingSession.objects.get(user=request.user)
    except OnboardingSession.DoesNotExist:
        return Response(
            {'message': 'Onboarding session not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if session.is_completed:
        return Response({'message': 'Onboarding already completed!'})

    step = request.data.get('step')

    if step == 1:
        session.step_1_completed = True
        session.current_step = 2
    elif step == 2:
        session.step_2_completed = True
        session.current_step = 3
    elif step == 3:
        session.step_3_completed = True
        session.current_step = 4
    elif step == 4:
        session.step_4_completed = True
        session.current_step = 5
    elif step == 5:
        session.step_5_completed = True
        session.is_completed = True
        session.completed_at = timezone.now()
        session.current_step = 5

        # Fix: message field is required in RewardNotificationQueue
        RewardNotificationQueue.objects.create(
            user=request.user,
            message='Welcome! Your first reward is ready. Start recycling to earn points!',
        )

        session.save()
        return Response({
            'message': 'Onboarding complete! First reward notification queued.',
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'message': 'Invalid step!'},
            status=status.HTTP_400_BAD_REQUEST
        )

    session.save()
    return Response({
        'message': f'Step {step} completed!',
        'next_step': session.current_step,
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
        return Response(
            {'message': 'No onboarding session found'},
            status=status.HTTP_404_NOT_FOUND
        )


# SNOOZE OR STOP PROMPTS
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manage_prompts(request):
    from users.models import UserPromptSettings
    from datetime import timedelta

    action = request.data.get('action')
    settings_obj, _ = UserPromptSettings.objects.get_or_create(user=request.user)

    if action == 'stop':
        settings_obj.is_active = False
        settings_obj.frequency = 'stopped'
        settings_obj.save()
        return Response({'message': 'Prompts stopped successfully!'})

    elif action == 'snooze':
        settings_obj.snoozed_until = timezone.now() + timedelta(days=7)
        settings_obj.save()
        return Response({'message': 'Prompts snoozed for 7 days!'})

    elif action == 'resume':
        settings_obj.is_active = True
        settings_obj.snoozed_until = None
        settings_obj.frequency = '3x_week'
        settings_obj.save()
        return Response({'message': 'Prompts resumed!'})

    return Response(
        {'error': 'Invalid action. Use stop, snooze or resume'},
        status=status.HTTP_400_BAD_REQUEST
    )

# ADD THIS FUNCTION AT THE BOTTOM OF users/views.py

@api_view(['POST'])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    phone   = request.data.get('From', '')
    message = request.data.get('Body', '').strip().lower()

    if 'hello' in message or 'hi' in message or message == '':
        reply = "Hello! Welcome to Ecosort Nigeria! 🌿\n\nReply with:\n1 - Request a pickup\n2 - Waste rates\n3 - Recycling tips\n4 - About Ecosort"

    elif '1' in message or 'request' in message or 'pickup' in message:
        reply = "To request a pickup:\n✅ Open the Ecosort app\n✅ Tap Request Pickup\n✅ Select waste type\n✅ Get your 6-digit code\n✅ Show code to collector!\n\nDownload: ecosorttech.netlify.app"

    elif '2' in message or 'rate' in message or 'price' in message:
        reply = "Current Ecosort rates:\n♻️ PET Plastic - ₦80/kg\n🔩 Aluminum - ₦360/kg\n📦 Carton - ₦40/kg\n📄 Paper - ₦20/kg\n🪟 Glass - ₦30/kg\n\nEarn points for every pickup!"

    elif '3' in message or 'learn' in message or 'recycle' in message or 'tip' in message:
        reply = "♻️ Recycling Tips:\n✅ Sort waste before pickup\n✅ Keep materials dry\n✅ Flatten cartons\n✅ Rinse plastic bottles\n✅ Separate metals from plastic\n\nEarn badges in the app!"

    elif '4' in message or 'about' in message or 'ecosort' in message:
        reply = "🌿 About Ecosort Nigeria\n\nEcosort connects households with waste collectors to make recycling easy and rewarding!\n\n✅ Request pickups\n✅ Earn points\n✅ Learn about recycling\n✅ Sell recyclables\n\nJoin us: ecosorttech.netlify.app"

    else:
        reply = "Welcome to Ecosort Nigeria! 🌿\n\nReply with:\n1 - Request a pickup\n2 - Waste rates\n3 - Recycling tips\n4 - About Ecosort\n\nVisit: ecosorttech.netlify.app"

    # Send reply via Twilio WhatsApp
    try:
        from twilio.rest import Client
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token  = os.environ.get('TWILIO_AUTH_TOKEN')
        from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=reply,
            from_=from_number,
            to=phone
        )
    except Exception as e:
        pass

    return Response({'status': 'ok'}, status=status.HTTP_200_OK)