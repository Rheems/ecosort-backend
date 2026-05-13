from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.create_pickup_request, name='create_pickup'),
    path('confirm/', views.confirm_pickup, name='confirm_pickup'),
    path('my-pickups/', views.get_my_pickups, name='my_pickups'),
]