from django.urls import path
from . import views

urlpatterns = [
    # Marketplace endpoints
    path('listings/', views.get_listings, name='get_listings'),
    path('listings/create/', views.create_listing, name='create_listing'),
    path('listings/my/', views.my_listings, name='my_listings'),
    path('listings/<int:listing_id>/', views.get_listing, name='get_listing'),
    path('listings/<int:listing_id>/buy/', views.buy_listing, name='buy_listing'),
    path('listings/<int:listing_id>/cancel/', views.cancel_listing, name='cancel_listing'),
    path('purchases/', views.my_purchases, name='my_purchases'),
    path('pricing/', views.get_pricing, name='get_pricing'),

    # USSD endpoint
    path('ussd/', views.ussd_handler, name='ussd_handler'),
]