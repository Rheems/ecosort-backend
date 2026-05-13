
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
import secrets
from .models import PickupRequest, ConfirmationCode
from .serializer import PickupRequestSerializer, ConfirmationCodeSerializer

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

    try:
        confirmation = ConfirmationCode.objects.get(code=code)
    except ConfirmationCode.DoesNotExist:
        return Response(
            {'error': 'Invalid confirmation code'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if already used
    if confirmation.is_used:
        return Response(
            {'error': 'Code already used'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if expired
    if timezone.now() > confirmation.expires_at:
        return Response(
            {'error': 'Code has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Credit points (10pts per kg)
    weight_kg = float(weight_kg)
    points = int(weight_kg * 10)

    # Update pickup
    pickup = confirmation.pickup
    pickup.weight_kg = weight_kg
    pickup.points_credited = points
    pickup.status = 'completed'
    pickup.save()

    # Mark code as used
    confirmation.is_used = True
    confirmation.save()

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