from django.http import JsonResponse
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.urls import path, include 
urlpatterns = [
    path('',
    include('myapp.urls')),
]
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

def homepage(request):
    return JsonResponse({
        "message": "Welcome to Ecosort API 🌿",
        "version": "v2.0",
        "team": "Team 3 Eco-Sorters",
        "status": "Live",
        "docs": "https://rheems.github.io/ecosort-backend/",
        "github": "https://github.com/Rheems/ecosort-backend",
        "interactive_docs": "/api/docs/",
        "redoc": "/api/redoc/",
        "endpoints": {
            "authentication": {
                "register": "POST /api/auth/register/",
                "login": "POST /api/auth/login/",
                "request_otp": "POST /api/auth/request-otp/",
                "verify_otp": "POST /api/auth/verify-otp/",
            },
            "profile": {
                "get_profile": "GET /api/profile/me/",
                "update_profile": "PUT /api/profile/me/",
            },
            "onboarding": {
                "status": "GET /api/onboarding/status/",
                "complete_step": "POST /api/onboarding/complete/",
            },

            "education": {
    "all_guides": "GET /api/education/guides/",
    "category_guide": "GET /api/education/guides/<category>/",
    "submit_quiz": "POST /api/education/quiz/submit/",
    "my_results": "GET /api/education/quiz/results/",
},

    "pickup": {
    "create_pickup": "POST /api/pickup/request/",
    "confirm_pickup": "POST /api/pickup/confirm/",
    "my_pickups": "GET /api/pickup/my-pickups/",        
},

"marketplace": {
    "all_listings": "GET /api/marketplace/listings/",
    "create_listing": "POST /api/marketplace/listings/create/",
    "my_listings": "GET /api/marketplace/listings/my/",
    "single_listing": "GET /api/marketplace/listings/<id>/",
    "buy_listing": "POST /api/marketplace/listings/<id>/buy/",
    "cancel_listing": "POST /api/marketplace/listings/<id>/cancel/",
    "my_purchases": "GET /api/marketplace/purchases/",
    "pricing_guide": "GET /api/marketplace/pricing/",
    "ussd": "POST /api/marketplace/ussd/",
},

        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('', homepage, name='home'),
    path('api/education/', include('education.urls')),
    path('api/pickup/', include('pickup.urls')),
    path('api/marketplace/', include('marketplace.urls')),


]