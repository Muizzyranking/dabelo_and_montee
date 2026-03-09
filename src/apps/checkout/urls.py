from django.urls import path

from . import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/pay/", views.initialize_payment, name="checkout_pay"),
    path("checkout/verify/", views.verify_payment, name="checkout_verify"),
    path("checkout/webhook/", views.paystack_webhook, name="paystack_webhook"),
    path(
        "checkout/confirmation/<str:order_number>/",
        views.order_confirmation,
        name="order_confirmation",
    ),
]
