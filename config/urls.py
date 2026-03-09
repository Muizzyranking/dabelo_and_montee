from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from django.conf.urls import handler404, handler500

from config import settings

handler404 = "core.views.page_not_found"
handler500 = "core.views.server_error"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("shop/", include("products.urls")),
    path("", include("accounts.urls")),
    path("", include("cart.urls")),
    path("", include("checkout.urls")),
    path("", include("admin_panel.urls")),
    path("images/", include("images.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
