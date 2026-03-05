from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum
from decimal import Decimal

User = get_user_model()


class Cart(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="cart"
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session_key"],
                condition=models.Q(session_key__isnull=False),
                name="unique_session_cart",
            )
        ]

    def __str__(self):
        return f"Cart({self.user or self.session_key})"

    @property
    def total_items(self):
        return self.items.aggregate(total=Sum("quantity"))["total"] or 0

    @property
    def subtotal(self):
        total = Decimal("0")
        for item in self.items.select_related("product", "variation"):
            total += item.line_total
        return total

    def merge_with(self, other_cart):
        """
        Merge other_cart into self.
        Called when anonymous user logs in.
        """
        for item in other_cart.items.select_related("product", "variation"):
            existing = self.items.filter(
                product=item.product, variation=item.variation
            ).first()
            if existing:
                existing.quantity += item.quantity
                existing.save()
            else:
                item.cart = self
                item.pk = None
                item.save()
        other_cart.delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    variation = models.ForeignKey(
        "products.ProductVariation", on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["added_at"]
        unique_together = [("cart", "product", "variation")]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def unit_price(self):
        if self.variation and self.variation.price:
            return self.variation.price
        return self.product.display_price or Decimal("0")

    @property
    def line_total(self):
        return self.unit_price * self.quantity
