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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    language_preference = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='english')
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='app')
    updated_at = models.DateTimeField(auto_now=True)

class OnboardingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, default='first_reward')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    queued_at = models.DateTimeField(auto_now_add=True)



# Create your models here.
