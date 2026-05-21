
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

from .models import MaterialListing, MarketplaceTransaction, PricingReference, USSDSession
from .serializers import (
    MaterialListingSerializer,
    CreateListingSerializer,
    MarketplaceTransactionSerializer,
    PricingReferenceSerializer
)


# ── GET ALL ACTIVE LISTINGS ──
@api_view(['GET'])
@permission_classes([AllowAny])
def get_listings(request):
    # Auto-expire old listings
    MaterialListing.objects.filter(
        expires_at__lt=timezone.now(),
        status='active'
    ).update(status='expired')

    material_type = request.query_params.get('material_type', None)
    listings = MaterialListing.objects.filter(status='active')

    if material_type:
        listings = listings.filter(material_type=material_type)

    listings = listings.order_by('-created_at')
    serializer = MaterialListingSerializer(listings, many=True)
    return Response(serializer.data)


# ── CREATE LISTING ──
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_listing(request):
    serializer = CreateListingSerializer(data=request.data)
    if serializer.is_valid():
        listing = serializer.save(
            seller=request.user,
            channel='app'
        )
        return Response({
            'message': 'Listing created successfully!',
            'listing_id': listing.id,
            'material_type': listing.material_type,
            'quantity_kg': listing.quantity_kg,
            'price_per_kg': listing.price_per_kg,
            'total_price': listing.total_price,
            'expires_at': listing.expires_at,
            'note': 'Listing expires in 48 hours'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── GET MY LISTINGS ──
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_listings(request):
    listings = MaterialListing.objects.filter(
        seller=request.user
    ).order_by('-created_at')
    serializer = MaterialListingSerializer(listings, many=True)
    return Response(serializer.data)


# ── GET SINGLE LISTING ──
@api_view(['GET'])
@permission_classes([AllowAny])
def get_listing(request, listing_id):
    try:
        listing = MaterialListing.objects.get(id=listing_id)
        serializer = MaterialListingSerializer(listing)
        return Response(serializer.data)
    except MaterialListing.DoesNotExist:
        return Response(
            {'error': 'Listing not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# ── BUY / EXPRESS INTEREST ──
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_listing(request, listing_id):
    try:
        listing = MaterialListing.objects.get(id=listing_id, status='active')
    except MaterialListing.DoesNotExist:
        return Response(
            {'error': 'Listing not found or no longer available'},
            status=status.HTTP_404_NOT_FOUND
        )

    if listing.seller == request.user:
        return Response(
            {'error': 'You cannot buy your own listing'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if listing.is_expired():
        listing.status = 'expired'
        listing.save()
        return Response(
            {'error': 'This listing has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create transaction
    transaction = MarketplaceTransaction.objects.create(
        listing=listing,
        buyer=request.user,
        quantity_kg=listing.quantity_kg,
        total_paid=listing.total_price,
        status='pending'
    )

    # Mark listing as sold
    listing.status = 'sold'
    listing.save()

    return Response({
        'message': 'Purchase successful! Contact seller to arrange pickup.',
        'transaction_id': transaction.id,
        'material_type': listing.material_type,
        'quantity_kg': listing.quantity_kg,
        'total_paid': listing.total_price,
        'seller_phone': listing.seller.phone_number,
        'location': listing.location,
    }, status=status.HTTP_201_CREATED)


# ── CANCEL LISTING ──
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_listing(request, listing_id):
    try:
        listing = MaterialListing.objects.get(
            id=listing_id,
            seller=request.user,
            status='active'
        )
        listing.status = 'cancelled'
        listing.save()
        return Response({'message': 'Listing cancelled successfully!'})
    except MaterialListing.DoesNotExist:
        return Response(
            {'error': 'Listing not found or already inactive'},
            status=status.HTTP_404_NOT_FOUND
        )


# ── GET MY PURCHASES ──
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_purchases(request):
    transactions = MarketplaceTransaction.objects.filter(
        buyer=request.user
    ).order_by('-created_at')
    serializer = MarketplaceTransactionSerializer(transactions, many=True)
    return Response(serializer.data)


# ── GET PRICING REFERENCE ──
@api_view(['GET'])
@permission_classes([AllowAny])
def get_pricing(request):
    prices = PricingReference.objects.all()
    serializer = PricingReferenceSerializer(prices, many=True)
    return Response(serializer.data)


# ── USSD ENDPOINT ──
@csrf_exempt
def ussd_handler(request):
    if request.method == 'POST':
        session_id = request.POST.get('sessionId', '')
        phone_number = request.POST.get('phoneNumber', '')
        text = request.POST.get('text', '')

        # Get or create session
        session, created = USSDSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'phone_number': phone_number,
                'current_menu': 'main',
                'session_data': {}
            }
        )

        # Parse user input
        parts = text.split('*') if text else []
        level = len(parts)

        response = process_ussd_menu(session, text, parts, level, phone_number)
        return HttpResponse(response, content_type='text/plain')

    return HttpResponse('Method not allowed', status=405)


def process_ussd_menu(session, text, parts, level, phone_number):
    # MAIN MENU
    if text == '':
        return """CON Welcome to Ecosort 🌿
1. View Listings
2. Create Listing
3. My Listings
4. Pricing Guide
5. My Account"""

    # LEVEL 1
    if level == 1:
        choice = parts[0]

        if choice == '1':
            return """CON Select material:
1. Plastic
2. Paper
3. Glass
4. Metal
5. Organic
6. All Materials"""

        elif choice == '2':
            return """CON Select material to sell:
1. Plastic
2. Paper
3. Glass
4. Metal
5. Organic"""

        elif choice == '3':
            try:
                from users.models import User
                user = User.objects.get(phone_number=phone_number)
                listings = MaterialListing.objects.filter(
                    seller=user,
                    status='active'
                ).order_by('-created_at')[:5]

                if not listings:
                    return "END You have no active listings."

                response = "CON Your active listings:\n"
                for i, l in enumerate(listings, 1):
                    response += f"{i}. {l.material_type} - {l.quantity_kg}kg @ ₦{l.price_per_kg}/kg\n"
                return response
            except:
                return "END Account not found. Please register on the app."

        elif choice == '4':
            prices = PricingReference.objects.all()
            if not prices:
                return """END Current prices (per kg):
Plastic: ₦80-100
Paper: ₦30-50
Glass: ₦20-40
Metal: ₦500-600
Organic: ₦10-20"""

            response = "END Current prices (per kg):\n"
            for p in prices:
                response += f"{p.material_type.title()}: ₦{p.min_price_per_kg}-{p.max_price_per_kg}\n"
            return response

        elif choice == '5':
            try:
                from users.models import User
                user = User.objects.get(phone_number=phone_number)
                from pickup.models import PickupRequest
                from django.db.models import Sum
                total_points = PickupRequest.objects.filter(
                    user=user, status='completed'
                ).aggregate(total=Sum('points_credited'))['total'] or 0
                return f"END Account Info:\nPhone: {phone_number}\nPoints: {total_points}\nVisit app for more details."
            except:
                return "END Account not found. Please register on the app."

    # LEVEL 2 — VIEW LISTINGS by material
    if level == 2 and parts[0] == '1':
        material_map = {
            '1': 'plastic', '2': 'paper',
            '3': 'glass', '4': 'metal',
            '5': 'organic'
        }
        choice = parts[1]

        if choice == '6':
            listings = MaterialListing.objects.filter(status='active')[:5]
        else:
            material = material_map.get(choice)
            if not material:
                return "END Invalid choice."
            listings = MaterialListing.objects.filter(
                status='active', material_type=material
            )[:5]

        if not listings:
            return "END No active listings found."

        response = "END Available listings:\n"
        for l in listings:
            response += f"- {l.material_type} {l.quantity_kg}kg @ ₦{l.price_per_kg}/kg | {l.location}\n"
        return response

    # LEVEL 2 — CREATE LISTING: select quantity
    if level == 2 and parts[0] == '2':
        material_map = {
            '1': 'plastic', '2': 'paper',
            '3': 'glass', '4': 'metal',
            '5': 'organic'
        }
        material = material_map.get(parts[1])
        if not material:
            return "END Invalid material choice."

        session.session_data['material'] = material
        session.save()
        return f"CON Enter quantity in kg for {material}:"

    # LEVEL 3 — CREATE LISTING: enter price
    if level == 3 and parts[0] == '2':
        try:
            quantity = float(parts[2])
            session.session_data['quantity'] = quantity
            session.save()
            return "CON Enter price per kg in Naira (₦):"
        except:
            return "END Invalid quantity. Please enter a number."

    # LEVEL 4 — CREATE LISTING: confirm
    if level == 4 and parts[0] == '2':
        try:
            price = float(parts[3])
            material = session.session_data.get('material', '')
            quantity = session.session_data.get('quantity', 0)
            total = quantity * price

            session.session_data['price'] = price
            session.save()

            return f"""CON Confirm listing:
Material: {material}
Quantity: {quantity}kg
Price: ₦{price}/kg
Total: ₦{total}
1. Confirm
2. Cancel"""
        except:
            return "END Invalid price. Please enter a number."

    # LEVEL 5 — CREATE LISTING: save
    if level == 5 and parts[0] == '2':
        choice = parts[4]
        if choice == '1':
            try:
                from users.models import User
                user = User.objects.get(phone_number=phone_number)
                material = session.session_data.get('material')
                quantity = session.session_data.get('quantity')
                price = session.session_data.get('price')

                listing = MaterialListing.objects.create(
                    seller=user,
                    material_type=material,
                    quantity_kg=quantity,
                    price_per_kg=price,
                    location=user.userprofile.location or 'Nigeria',
                    channel='ussd'
                )

                session.is_active = False
                session.save()

                return f"END Listing created!\n{material} {quantity}kg @ ₦{price}/kg\nListing ID: {listing.id}\nExpires in 48 hours."
            except Exception as e:
                return f"END Error creating listing. Please try again."
        else:
            return "END Listing cancelled."

    return "END Invalid input. Please try again."