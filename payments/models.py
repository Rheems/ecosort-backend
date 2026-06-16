from django.db import models
from django.conf import settings


class PaymentAccount(models.Model):
    VERIFICATION_STATUS = [
        ("PENDING", "Pending"),
        ("VERIFIED", "Verified"),
        ("FAILED", "Failed"),
        ("REMOVED", "Removed"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_account"
    )
    bank_code = models.CharField(max_length=10)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=10)
    account_name = models.CharField(max_length=200)
    recipient_code = models.CharField(max_length=100, blank=True, null=True)
    verification_status = models.CharField(
        max_length=10, choices=VERIFICATION_STATUS, default="PENDING"
    )
    is_primary = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "account_number", "bank_code")

    def __str__(self):
        return f"{self.user} - {self.bank_name} ({self.account_number[-4:]})"


class PickupPaymentLink(models.Model):
    pickup_id = models.IntegerField(unique=True)
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pickup_payments_initiated"
    )
    household = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pickup_payments_received"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pickup {self.pickup_id} Payment Link"


class Payment(models.Model):
    PAYMENT_STATUS = [
        ("INITIATED", "Initiated"),
        ("PROCESSING", "Processing"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("RETRYING", "Retrying"),
        ("REVERSED", "Reversed"),
    ]

    pickup = models.OneToOneField(
        PickupPaymentLink,
        on_delete=models.CASCADE,
        related_name="payment",
        null=True,
        blank=True,
    )
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments_sent"
    )
    household = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments_received"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    payment_status = models.CharField(
        max_length=15, choices=PAYMENT_STATUS, default="INITIATED"
    )
    provider_reference = models.CharField(max_length=200, blank=True, null=True)
    transfer_code = models.CharField(max_length=200, blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} - {self.collector} → {self.household} | {self.payment_status}"