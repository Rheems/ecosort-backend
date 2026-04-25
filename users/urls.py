from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('profile/me/', views.profile, name='profile'),
    path('onboarding/complete/', views.complete_onboarding, name='complete_onboarding'),
    path('onboarding/status/', views.onboarding_status, name='onboarding_status'),
]