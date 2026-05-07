from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# A simple view to show something on the home page
def home_view(request):
    return HttpResponse("<h1>Ecosort API is Live</h1><p>Go to <a href='/api/'>/api/</a> to see the endpoints.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('', home_view), # This fixes the 404 on the main link!
]
