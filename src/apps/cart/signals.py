from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .service import merge_carts_on_login


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    merge_carts_on_login(request, user)
