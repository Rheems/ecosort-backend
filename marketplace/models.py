from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def default_expiry():
    return timezone.now() + timedelta(hours=48)


class MaterialListing(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    MATERIAL_CHOICES = [
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('glass', 'Glass'),
        ('metal', 'Metal'),
        ('organic', 'Organic'),
    ]

    CHANNEL_CHOICES = [
        ('app', 'App'),
        ('ussd', 'USSD'),
        ('whatsapp', 'WhatsApp'),
    ]

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    material_type = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    quantity_kg = models.FloatField()
    price_per_kg = models.FloatField()
    total_price = models.FloatField(blank=True, null=True)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='app')
    expires_at = models.DateTimeField(default=default_expiry)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity_kg * self.price_per_kg
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.seller} - {self.material_type} - {self.quantity_kg}kg - {self.status}"


class MarketplaceTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    listing = models.ForeignKey(MaterialListing, on_delete=models.CASCADE, related_name='transactions')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    quantity_kg = models.FloatField()
    total_paid = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer} bought {self.quantity_kg}kg from {self.listing.seller}"


class PricingReference(models.Model):
    MATERIAL_CHOICES = [
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('glass', 'Glass'),
        ('metal', 'Metal'),
        ('organic', 'Organic'),
    ]

    material_type = models.CharField(max_length=20, choices=MATERIAL_CHOICES, unique=True)
    min_price_per_kg = models.FloatField()
    max_price_per_kg = models.FloatField()
    suggested_price_per_kg = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=100, default='V-Martins Lagos Market 2026')

    def __str__(self):
        return f"{self.material_type} - ₦{self.suggested_price_per_kg}/kg"


class USSDSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    current_menu = models.CharField(max_length=50, default='main')
    session_data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} - {self.current_menu}"

