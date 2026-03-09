from django.urls import path

from . import views

urlpatterns = [
    path("", views.shop_joint, name="shop"),
    path("dabelo/", views.shop_dabelo, name="shop_dabelo"),
    path("montee/", views.shop_montee, name="shop_montee"),
    path("category/<slug:slug>/", views.shop_category, name="shop_category"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("product/<slug:slug>/quote/", views.submit_quote, name="submit_quote"),
    path("custom-order/", views.custom_order_page, name="custom_order"),
    path(
        "custom-order/submit/", views.submit_general_quote, name="submit_general_quote"
    ),
]
