from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/request-otp/', views.request_otp, name='request_otp'),
    path('auth/verify-otp/', views.verify_otp, name='verify_otp'),
    path('profile/me/', views.profile, name='profile'),
    path('onboarding/complete/', views.complete_onboarding, name='complete_onboarding'),
    path('onboarding/status/', views.onboarding_status, name='onboarding_status'),path('profile/points/', views.get_points, name='points'),
    path('prompts/manage/', views.manage_prompts, name='manage_prompts'),
]