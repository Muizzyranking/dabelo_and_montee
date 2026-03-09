from django.urls import path

from . import views

urlpatterns = [
    path("serve/<uuid:image_id>/", views.serve_image, name="image_serve"),
]
