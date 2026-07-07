"""
URL configuration for deli project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import health

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path("health/", health),

    path("api/v1/users/", include("users.urls")),
    path("api/v1/restaurants/", include("restaurants.urls")),
    path("api/v1/orders/", include("orders.urls")),
    path("api/v1/cart/", include("cart.urls")),
    path("api/v1/payments/", include("payments.urls")),
    path("api/v1/delivery/", include("delivery.urls")),
    path("api/v1/whatsapp/", include("whatsapp.urls")),

    path("api/users/", include("users.urls")),
    path("api/restaurants/", include("restaurants.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/cart/", include("cart.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/delivery/", include("delivery.urls")),
    path("api/whatsapp/", include("whatsapp.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
