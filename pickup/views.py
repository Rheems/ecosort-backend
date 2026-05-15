from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
import secrets
import pickup.serializers as serializers
from .models import PickupRequest, ConfirmationCode, ConfirmationCodeLog
from .serializers import PickupRequestSerializer, ConfirmationCodeSerializer


# CREATE PICKUP REQUEST
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_pickup_request(request):
    serializer = PickupRequestSerializer(data=request.data)
    if serializer.is_valid():
        pickup = serializer.save(user=request.user)

        # Generate confirmation code
        code = secrets.token_hex(32)
        expires_at = timezone.now() + timedelta(hours=4)
        ConfirmationCode.objects.create(
            pickup=pickup,
            code=code,
            expires_at=expires_at
        )

        # Log code generation
        ConfirmationCodeLog.objects.create(
            pickup=pickup,
            code_used=code,
            status='generated',
            attempted_by=request.user,
            note='Confirmation code generated for pickup request'
        )

        return Response({
            'message': 'Pickup request created!',
            'pickup_id': pickup.id,
            'confirmation_code': code,
            'expires_at': expires_at,
            'note': 'Code expires in 4 hours'
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# CONFIRM PICKUP WITH CODE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_pickup(request):
    code = request.data.get('code')
    weight_kg = request.data.get('weight_kg')

    if not code or not weight_kg:
        return Response(
            {'error': 'code and weight_kg are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if code exists
    try:
        confirmation = ConfirmationCode.objects.get(code=code)
    except ConfirmationCode.DoesNotExist:
        # Log invalid attempt
        ConfirmationCodeLog.objects.create(
            pickup=None,
            code_used=code,
            status='invalid_attempt',
            attempted_by=request.user,
            note='Code not found in database'
        )
        return Response(
            {'error': 'Invalid confirmation code'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if already used
    if confirmation.is_used:
        ConfirmationCodeLog.objects.create(
            pickup=confirmation.pickup,
            code_used=code,
            status='invalid_attempt',
            attempted_by=request.user,
            note='Code already used'
        )
        return Response(
            {'error': 'Code already used'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if expired
    if timezone.now() > confirmation.expires_at:
        ConfirmationCodeLog.objects.create(
            pickup=confirmation.pickup,
            code_used=code,
            status='expired',
            attempted_by=request.user,
            note='Code expired'
        )
        return Response(
            {'error': 'Code has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # All checks passed — confirm pickup
    weight_kg = float(weight_kg)
    points = int(weight_kg * 10)

    pickup = confirmation.pickup
    pickup.weight_kg = weight_kg
    pickup.points_credited = points
    pickup.status = 'completed'
    pickup.save()

    # Mark code as used
    confirmation.is_used = True
    confirmation.save()

    # Log successful confirmation
    ConfirmationCodeLog.objects.create(
        pickup=pickup,
        code_used=code,
        status='confirmed',
        attempted_by=request.user,
        weight_kg=weight_kg,
        points_credited=points,
        note='Pickup successfully confirmed'
    )

    return Response({
        'message': 'Pickup confirmed!',
        'weight_kg': weight_kg,
        'points_credited': points,
        'pickup_status': 'completed'
    }, status=status.HTTP_200_OK)


# GET MY PICKUP REQUESTS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_pickups(request):
    pickups = PickupRequest.objects.filter(user=request.user).order_by('-created_at')
    serializer = PickupRequestSerializer(pickups, many=True)
    return Response(serializer.data)


# GET CONFIRMATION CODE LOGS (admin use)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_code_logs(request):
    logs = ConfirmationCodeLog.objects.filter(
        attempted_by=request.user
    ).order_by('-timestamp')

    data = [{
        'status': log.status,
        'weight_kg': log.weight_kg,
        'points_credited': log.points_credited,
        'timestamp': log.timestamp,
        'note': log.note,
    } for log in logs]

    return Response(data, status=status.HTTP_200_OK)