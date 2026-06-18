from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('household', 'Household'),
        ('collector', 'Collector'),
        ('buyer', 'Buyer'),
        ('brand', 'Brand'),
    ]
    phone_number = models.CharField(max_length=20, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='household')
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email']

    def __str__(self):
        return f"{self.phone_number} ({self.user_type})"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    language_preference = models.CharField(max_length=20, default='english')
    channel = models.CharField(max_length=20, default='app')
    waste_type = models.CharField(max_length=20, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} profile"


class OTPVerification(models.Model):
    phone_number = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone_number} - {self.otp}"


class OnboardingSession(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_step = models.IntegerField(default=1)
    step_1_completed = models.BooleanField(default=False)
    step_2_completed = models.BooleanField(default=False)
    step_3_completed = models.BooleanField(default=False)
    step_4_completed = models.BooleanField(default=False)
    step_5_completed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} onboarding"


class RewardNotificationQueue(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.message[:50]}"


class UserPromptSettings(models.Model):
    FREQUENCY_CHOICES = [
        ('3x_week', '3x per week'),
        ('1x_week', '1x per week'),
        ('stopped', 'Stopped'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='3x_week')
    is_active = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    snoozed_until = models.DateTimeField(null=True, blank=True)
    last_prompt_sent = models.DateTimeField(null=True, blank=True)
    last_category_sent = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user} - {self.frequency}"