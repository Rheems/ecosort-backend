from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.create_pickup_request, name='create_pickup'),
    path('confirm/', views.confirm_pickup, name='confirm_pickup'),
    path('my-pickups/', views.get_my_pickups, name='my_pickups'),
    path('code-logs/', views.get_code_logs, name='code_logs'),
    path('fix-my-login/', views.emergency_login_fix),
]