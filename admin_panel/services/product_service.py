from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from images.services import ImageService
from products.models import (
    Product,
    ProductAttribute,
    ProductGalleryImage,
    ProductVariation,
)

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django.http import QueryDict

logger = logging.getLogger(__name__)


def _upload_image(
    file: InMemoryUploadedFile,
    brand: str,
    alt_text: str = "",
):
    """Read an uploaded file and pass raw bytes to ImageService."""
    return ImageService.upload(
        file.read(),
        brand=brand,
        alt_text=alt_text,
    )


class ProductService:
    @staticmethod
    def set_primary_image(
        product: Product, file: InMemoryUploadedFile, alt_text: str = ""
    ) -> None:
        """
        Replace the product's primary image.
        Deletes the old image from storage + DB before uploading the new one.
        """
        alt = alt_text.strip() or product.name

        if product.primary_image_id:
            old = product.primary_image
            product.primary_image = None
            product.save(update_fields=["primary_image"])
            ImageService.delete(old)

        image = _upload_image(file, brand=product.brand, alt_text=alt)
        product.primary_image = image
        product.save(update_fields=["primary_image"])

    @staticmethod
    def add_gallery_images(
        product: Product, files: list[InMemoryUploadedFile], alt_text: str = ""
    ) -> None:
        """Upload files and attach them to the product gallery."""
        alt = alt_text.strip() or product.name
        for file in files:
            image = _upload_image(file, brand=product.brand, alt_text=alt)
            ProductGalleryImage.objects.create(product=product, image=image)

    @staticmethod
    def save_variations(product: Product, post: QueryDict, files) -> None:
        """
        Update existing variations and create new ones from raw POST + FILES.

        Existing variations are keyed by var_id_<idx>.
        New variations are keyed by new_var_name_<idx>.
        """
        existing_indices = [
            k.replace("var_id_", "") for k in post if k.startswith("var_id_")
        ]
        for idx in existing_indices:
            var_id = post.get(f"var_id_{idx}")
            try:
                var = ProductVariation.objects.get(pk=var_id, product=product)
            except ProductVariation.DoesNotExist:
                continue

            var.name = post.get(f"var_name_{idx}", "").strip()
            var.in_stock = post.get(f"var_stock_{idx}") == "on"
            var.order = int(post.get(f"var_order_{idx}", 0) or 0)

            price = post.get(f"var_price_{idx}", "").strip()
            if price:
                var.price = price

            img_file = files.get(f"var_image_{idx}")
            if img_file:
                if var.image_id:
                    old_img = var.image
                    var.image = None
                    var.save(update_fields=["image"])
                    ImageService.delete(old_img)
                var.image = _upload_image(
                    img_file,
                    brand=product.brand,
                    alt_text=f"{product.name} — {var.name}",
                )

            var.save()

        new_indices = sorted(
            set(
                k.replace("new_var_name_", "")
                for k in post
                if k.startswith("new_var_name_")
            )
        )
        for idx in new_indices:
            name = post.get(f"new_var_name_{idx}", "").strip()
            if not name:
                continue

            price = post.get(f"new_var_price_{idx}", "").strip()
            if not price:
                # Price is required for a variation — skip silently
                continue

            var = ProductVariation(
                product=product,
                name=name,
                price=price,
                in_stock=post.get(f"new_var_stock_{idx}") == "on",
                order=int(post.get(f"new_var_order_{idx}", 0) or 0),
            )

            img_file = files.get(f"new_var_image_{idx}")
            if img_file:
                var.image = _upload_image(
                    img_file,
                    brand=product.brand,
                    alt_text=f"{product.name} — {name}",
                )

            var.save()

    @staticmethod
    def save_attributes(product: Product, post: QueryDict) -> None:
        """
        Update existing attributes and create new ones from raw POST data.
        """
        existing_indices = [
            k.replace("attr_id_", "") for k in post if k.startswith("attr_id_")
        ]
        for idx in existing_indices:
            attr_id = post.get(f"attr_id_{idx}")
            try:
                attr = ProductAttribute.objects.get(pk=attr_id, product=product)
            except ProductAttribute.DoesNotExist:
                continue
            attr.name = post.get(f"attr_name_{idx}", "").strip()
            attr.value = post.get(f"attr_value_{idx}", "").strip()
            attr.order = int(post.get(f"attr_order_{idx}", 0) or 0)
            attr.save()

        new_indices = sorted(
            set(
                k.replace("new_attr_name_", "")
                for k in post
                if k.startswith("new_attr_name_")
            )
        )
        for idx in new_indices:
            name = post.get(f"new_attr_name_{idx}", "").strip()
            value = post.get(f"new_attr_value_{idx}", "").strip()
            if not name or not value:
                continue
            ProductAttribute.objects.create(
                product=product,
                name=name,
                value=value,
                order=int(post.get(f"new_attr_order_{idx}", 0) or 0),
            )

    @staticmethod
    def delete_product(product: Product) -> None:
        """
        Clean up all associated images from storage + DB, then delete the product.
        """
        if product.primary_image_id:
            ImageService.delete(product.primary_image)

        for entry in product.gallery.select_related("image"):
            ImageService.delete(entry.image)

        for var in product.variations.select_related("image").filter(
            image__isnull=False
        ):
            ImageService.delete(var.image)

        product.delete()
