from __future__ import annotations

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Category, Product, ProductVariation
from .services import (
    invalidate_all_product_cache,
    invalidate_product_cache,
    invalidate_shop_cache,
)


def _bust_shop_and_product(slug: str | None = None) -> None:
    invalidate_shop_cache()
    if slug:
        invalidate_product_cache(slug)
    else:
        invalidate_all_product_cache()


@receiver([post_save, post_delete], sender=Product)
def on_product_change(sender, instance, **kwargs):
    _bust_shop_and_product(slug=instance.slug)


@receiver([post_save, post_delete], sender=ProductVariation)
def on_variation_change(sender, instance, **kwargs):
    _bust_shop_and_product(slug=instance.product.slug)


@receiver([post_save, post_delete], sender=Category)
def on_category_change(sender, instance, **kwargs):
    invalidate_shop_cache()
