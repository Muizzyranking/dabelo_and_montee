from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AdminProfile(models.Model):
    """Extended permissions for staff users."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="admin_profile"
    )
    is_superadmin = models.BooleanField(default=False)

    # Dabelo products
    can_view_dabelo_products = models.BooleanField(default=False)
    can_edit_dabelo_products = models.BooleanField(default=False)

    # Montee products
    can_view_montee_products = models.BooleanField(default=False)
    can_edit_montee_products = models.BooleanField(default=False)

    # Orders
    can_view_orders = models.BooleanField(default=False)
    can_edit_orders = models.BooleanField(default=False)

    # Quotes
    can_view_quotes = models.BooleanField(default=False)
    can_edit_quotes = models.BooleanField(default=False)

    # Images (within product edit)
    can_manage_images = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AdminProfile({self.user.email})"

    def has_any_product_access(self):
        return any(
            [
                self.can_view_dabelo_products,
                self.can_view_montee_products,
            ]
        )
