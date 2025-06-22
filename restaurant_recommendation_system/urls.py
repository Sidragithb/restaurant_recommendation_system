from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')), 
    path('api/menu/', include('menu.urls')),
    path('api/order/', include('order.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path("api/", include("recommender.urls")),
    path("api/outlet/", include("outlet.urls")),
    path("qr/", include("qr_code.urls")),    


 # Include user authentication URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
