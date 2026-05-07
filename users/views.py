from .models import User, UserProfile, OnboardingSession, RewardNotificationQueue, OTPVerification
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
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
        return Response({'error': 'Invalid phone number or password'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(password):
        return Response({'error': 'Invalid phone number or password'}, status=status.HTTP_400_BAD_REQUEST)

    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'message': 'Login successful!',
        'token': token.key,
        'user_id': user.id,
        'user_type': user.user_type,
    })


# REQUEST OTP
@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    phone_number = request.data.get('phone_number')

    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return Response({'error': 'No account found with this phone number'}, status=status.HTTP_404_NOT_FOUND)

    import random
    otp = str(random.randint(1000, 9999))

    OTPVerification.objects.create(user=user, otp=otp)

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
        return Response({'error': 'No account found with this phone number'}, status=status.HTTP_404_NOT_FOUND)

    try:
        otp_record = OTPVerification.objects.filter(
            user=user,
            is_used=False
        ).latest('created_at')
    except OTPVerification.DoesNotExist:
        return Response({'error': 'No OTP found. Please request a new one'}, status=status.HTTP_404_NOT_FOUND)

    if not otp_record.is_valid():
        return Response({'error': 'OTP has expired. Please request a new one'}, status=status.HTTP_400_BAD_REQUEST)

    if otp_record.otp != otp:
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

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

        RewardNotificationQueue.objects.create(
            user=request.user,
            notification_type='first_reward',
            status='pending',
        )

        session.save()
        return Response({
            'message': 'Onboarding complete! First reward notification queued.',
        }, status=status.HTTP_200_OK)

    else:
        return Response({'message': 'Invalid step!'}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({'message': 'No onboarding session found'}, status=status.HTTP_404_NOT_FOUND)

        # REQUEST OTP
@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    phone_number = request.data.get('phone_number')

    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return Response({'error': 'No account found with this phone number'}, status=status.HTTP_404_NOT_FOUND)

    # Generate 4 digit OTP
    import random
    otp = str(random.randint(1000, 9999))

    # Save OTP to database
    OTPVerification.objects.create(user=user, otp=otp)

    # In production this is where you send via Termii SMS
    # For now we return it in the response for testing
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
        return Response({'error': 'No account found with this phone number'}, status=status.HTTP_404_NOT_FOUND)

    # Get latest OTP for this user
    try:
        otp_record = OTPVerification.objects.filter(
            user=user,
            is_used=False
        ).latest('created_at')
    except OTPVerification.DoesNotExist:
        return Response({'error': 'No OTP found. Please request a new one'}, status=status.HTTP_404_NOT_FOUND)

    # Check if OTP is valid
    if not otp_record.is_valid():
        return Response({'error': 'OTP has expired. Please request a new one'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if OTP matches
    if otp_record.otp != otp:
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

    # Mark OTP as used
    otp_record.is_used = True
    otp_record.save()

    # Generate token
    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'message': 'OTP verified! Login successful!',
        'token': token.key,
        'user_id': user.id,
        'user_type': user.user_type,
    }, status=status.HTTP_200_OK)
