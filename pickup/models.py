from django.db import models
from django.conf import settings
import secrets

class PickupRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    waste_type = models.CharField(max_length=20)
    weight_kg = models.FloatField(default=0)
    points_credited = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class ConfirmationCode(models.Model):
    pickup = models.OneToOneField(PickupRequest, on_delete=models.CASCADE)
    code = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        return secrets.token_hex(32)

    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at

