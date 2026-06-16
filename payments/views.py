import hashlib
import hmac
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from . import paystack
from .models import Payment, PaymentAccount, PickupPaymentLink
from .serializers import (
    BankAccountInputSerializer,
    InitiatePaymentSerializer,
    PaymentAccountSerializer,
    PaymentSerializer,
)

User = get_user_model()


# ─────────────────────────────────────────────
# GET /api/payments/banks/
# ─────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def get_banks(request):
    result = paystack.get_banks()
    if result.get("status"):
        banks = [
            {"bank_code": b["code"], "bank_name": b["name"]}
            for b in result["data"]
        ]
        return Response({"status": "success", "banks": banks})
    return Response(
        {"status": "error", "message": "Could not fetch bank list."},
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


# ─────────────────────────────────────────────
# POST /api/payments/verify-account/
# ─────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_account(request):
    serializer = BankAccountInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    bank_code = serializer.validated_data["bank_code"]
    account_number = serializer.validated_data["account_number"]

    result = paystack.verify_account(account_number, bank_code)

    if result.get("status"):
        return Response({
            "status": "success",
            "account_name": result["data"]["account_name"],
            "account_number": account_number,
            "bank_code": bank_code,
        })

    return Response(
        {"status": "error", "message": "We could not verify this account. Please check your account number and try again."},
        status=status.HTTP_400_BAD_REQUEST,
    )


# ─────────────────────────────────────────────
# POST /api/payments/bank-account/
# ─────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_bank_account(request):
    user = request.user
    bank_code = request.data.get("bank_code")
    account_number = request.data.get("account_number")
    account_name = request.data.get("account_name")
    bank_name = request.data.get("bank_name")

    if not all([bank_code, account_number, account_name, bank_name]):
        return Response(
            {"status": "error", "message": "All fields are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Duplicate check
    existing = PaymentAccount.objects.filter(
        user=user, account_number=account_number, bank_code=bank_code
    ).first()
    if existing and existing.verification_status == "VERIFIED":
        return Response(
            {"status": "error", "message": "This account is already linked to your profile."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Register as Paystack transfer recipient
    recipient_result = paystack.create_transfer_recipient(account_name, account_number, bank_code)
    recipient_code = None
    if recipient_result.get("status"):
        recipient_code = recipient_result["data"]["recipient_code"]

    account, created = PaymentAccount.objects.update_or_create(
        user=user,
        defaults={
            "bank_code": bank_code,
            "bank_name": bank_name,
            "account_number": account_number,
            "account_name": account_name,
            "recipient_code": recipient_code,
            "verification_status": "VERIFIED",
            "is_primary": True,
        },
    )

    return Response(
        {
            "status": "success",
            "message": "Your bank account has been linked successfully. You can now receive payments.",
            "account": PaymentAccountSerializer(account).data,
        },
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


# ─────────────────────────────────────────────
# GET /api/payments/bank-account/me/
# ─────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_bank_account(request):
    try:
        account = request.user.payment_account
        return Response({"status": "success", "account": PaymentAccountSerializer(account).data})
    except PaymentAccount.DoesNotExist:
        return Response(
            {"status": "error", "message": "No payment account linked. Please add your bank account."},
            status=status.HTTP_404_NOT_FOUND,
        )


# ─────────────────────────────────────────────
# DELETE /api/payments/bank-account/remove/
# ─────────────────────────────────────────────
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_bank_account(request):
    try:
        account = request.user.payment_account
        pending = Payment.objects.filter(
            household=request.user,
            payment_status__in=["INITIATED", "PROCESSING", "RETRYING"],
        ).exists()
        if pending:
            return Response(
                {"status": "error", "message": "You have a pending payment. Account removal is locked until it completes."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        account.verification_status = "REMOVED"
        account.save()
        return Response({"status": "success", "message": "Your bank account has been removed."})
    except PaymentAccount.DoesNotExist:
        return Response(
            {"status": "error", "message": "No payment account found."},
            status=status.HTTP_404_NOT_FOUND,
        )


# ─────────────────────────────────────────────
# POST /api/payments/initiate/
# ─────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    serializer = InitiatePaymentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    collector = request.user
    pickup_id = serializer.validated_data["pickup_id"]
    household_id = serializer.validated_data["household_id"]
    amount = serializer.validated_data["amount"]

    # Duplicate payment check
    if PickupPaymentLink.objects.filter(pickup_id=pickup_id).exists():
        return Response(
            {"status": "error", "message": "A payment for this pickup is already being processed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get household user
    try:
        household = User.objects.get(id=household_id)
    except User.DoesNotExist:
        return Response(
            {"status": "error", "message": "Household user not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Check household has verified payment account
    try:
        hh_account = household.payment_account
        if hh_account.verification_status != "VERIFIED":
            raise PaymentAccount.DoesNotExist
    except PaymentAccount.DoesNotExist:
        return Response(
            {"status": "error", "message": "This household has not set up a payment account yet. Ask them to add their bank account on Ecosort."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not hh_account.recipient_code:
        return Response(
            {"status": "error", "message": "Household payment account is not properly configured. Please contact support."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create pickup payment link
    link = PickupPaymentLink.objects.create(
        pickup_id=pickup_id,
        collector=collector,
        household=household,
        amount=amount,
    )

    # Create payment record
    payment = Payment.objects.create(
        pickup=link,
        collector=collector,
        household=household,
        amount=amount,
        payment_status="INITIATED",
    )

    # Initiate Paystack transfer
    result = paystack.initiate_transfer(
        amount=amount,
        recipient_code=hh_account.recipient_code,
        reason=f"Ecosort pickup payment - Pickup #{pickup_id}",
    )

    if result.get("status"):
        payment.payment_status = "PROCESSING"
        payment.transfer_code = result["data"].get("transfer_code")
        payment.provider_reference = result["data"].get("reference")
        payment.save()
        return Response(
            {
                "status": "success",
                "message": f"Payment of NGN {amount} initiated successfully.",
                "payment_id": payment.id,
                "transfer_code": payment.transfer_code,
                "payment_status": "PROCESSING",
            },
            status=status.HTTP_201_CREATED,
        )
    else:
        payment.payment_status = "FAILED"
        payment.failure_reason = result.get("message", "Unknown error")
        payment.save()
        return Response(
            {"status": "error", "message": "Could not initiate payment. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )


# ─────────────────────────────────────────────
# POST /api/payments/retry/<payment_id>/
# ─────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def retry_payment(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id, collector=request.user)
    except Payment.DoesNotExist:
        return Response(
            {"status": "error", "message": "Payment not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if payment.payment_status != "FAILED":
        return Response(
            {"status": "error", "message": "This payment cannot be retried."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if payment.retry_count >= 3:
        return Response(
            {"status": "error", "message": "Maximum retry attempts reached. Our support team has been notified."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    hh_account = payment.household.payment_account
    payment.retry_count += 1
    payment.payment_status = "RETRYING"
    payment.save()

    result = paystack.initiate_transfer(
        amount=payment.amount,
        recipient_code=hh_account.recipient_code,
        reason=f"Ecosort retry #{payment.retry_count} - Payment #{payment.id}",
    )

    if result.get("status"):
        payment.payment_status = "PROCESSING"
        payment.transfer_code = result["data"].get("transfer_code")
        payment.provider_reference = result["data"].get("reference")
        payment.save()
        return Response({
            "status": "success",
            "message": f"Retrying payment (Attempt {payment.retry_count} of 3).",
            "payment_status": "PROCESSING",
        })
    else:
        payment.payment_status = "FAILED"
        payment.failure_reason = result.get("message")
        payment.save()
        return Response(
            {"status": "error", "message": "Retry failed. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )


# ─────────────────────────────────────────────
# GET /api/payments/my-payments/
# ─────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_payments(request):
    user = request.user
    sent = Payment.objects.filter(collector=user).order_by("-initiated_at")
    received = Payment.objects.filter(household=user).order_by("-initiated_at")
    return Response({
        "status": "success",
        "payments_sent": PaymentSerializer(sent, many=True).data,
        "payments_received": PaymentSerializer(received, many=True).data,
    })


# ─────────────────────────────────────────────
# POST /webhooks/paystack/
# ─────────────────────────────────────────────
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def paystack_webhook(request):
    paystack_signature = request.headers.get("X-Paystack-Signature")
    secret = settings.PAYSTACK_SECRET_KEY.encode("utf-8")
    body = request.body
    computed = hmac.new(secret, body, hashlib.sha512).hexdigest()

    if computed != paystack_signature:
        return Response({"status": "error"}, status=status.HTTP_401_UNAUTHORIZED)

    payload = json.loads(body)
    event = payload.get("event")
    data = payload.get("data", {})
    transfer_code = data.get("transfer_code")

    try:
        payment = Payment.objects.get(transfer_code=transfer_code)
    except Payment.DoesNotExist:
        return Response({"status": "ok"})

    if event == "transfer.success":
        payment.payment_status = "SUCCESS"
        payment.completed_at = timezone.now()
    elif event == "transfer.failed":
        payment.payment_status = "FAILED"
        payment.failure_reason = data.get("reason", "Transfer failed")
    elif event == "transfer.reversed":
        payment.payment_status = "REVERSED"
        payment.completed_at = timezone.now()

    payment.save()
    return Response({"status": "ok"})