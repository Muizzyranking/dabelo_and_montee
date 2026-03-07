from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from config import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("shop/", include("products.urls")),
    path("", include("accounts.urls")),
    path("", include("cart.urls")),
    path("", include("checkout.urls")),
    path("", include("admin_panel.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
