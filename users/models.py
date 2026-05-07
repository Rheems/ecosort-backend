from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('household', 'Household'),
        ('collector', 'Collector'),
        ('buyer', 'Buyer'),
        ('brand', 'Brand'),
    ]
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('english', 'English'),
        ('pidgin', 'Pidgin'),
    ]
    CHANNEL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('ussd', 'USSD'),
        ('app', 'App'),
    ]
    WASTE_TYPE_CHOICES = [
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('glass', 'Glass'),
        ('metal', 'Metal'),
        ('organic', 'Organic'),
        ('mixed', 'Mixed'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    language_preference = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='english')
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='app')
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPE_CHOICES, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)



class OnboardingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 5 individual steps
    step_1_completed = models.BooleanField(default=False)
    step_2_completed = models.BooleanField(default=False)
    step_3_completed = models.BooleanField(default=False)
    step_4_completed = models.BooleanField(default=False)
    step_5_completed = models.BooleanField(default=False)

    current_step = models.IntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

class RewardNotificationQueue(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
class OTPVerification(models.Model):
        user = models.ForeignKey (settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        otp = models.CharField(max_length=4)
        created_at = models.DateTimeField(auto_now_add=True)
        is_used = models.BooleanField(default=False)

def is_valid(self):
        from django.utils import timezone
        import datetime
        # OTP expires after 10 minutes
        expiry_time = self.created_at + datetime.timedelta(minutes=10)
        return timezone.now() < expiry_time and not self.is_used
        notification_type = models.CharField(max_length=50, default='first_reward')
        status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
        queued_at = models.DateTimeField(auto_now_add=True)

