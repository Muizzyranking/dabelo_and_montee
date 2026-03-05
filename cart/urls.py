from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart_page, name="cart"),
    path("cart/drawer/", views.cart_drawer, name="cart_drawer"),
    path("cart/count/", views.cart_count, name="cart_count"),
    path("cart/add/", views.add_to_cart, name="cart_add"),
    path("cart/update/", views.update_cart, name="cart_update"),
    path("cart/remove/", views.remove_from_cart, name="cart_remove"),
]
