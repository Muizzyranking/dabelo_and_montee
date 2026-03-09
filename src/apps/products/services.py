from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpRequest

from core.cache import CacheService

from .models import BrandChoices, Product

logger = logging.getLogger(__name__)

_shop_cache = CacheService("shop", default_ttl=60 * 15)  # 15 min
_product_cache = CacheService("product", default_ttl=60 * 15)  # 15 min

PRODUCTS_PER_PAGE = getattr(settings, "PRODUCTS_PER_PAGE", 12)


def _make_shop_key(brand: str, request: HttpRequest) -> str:
    """
    Stable cache key from brand + full sorted querystring.
    Different filter combinations → different keys.
    e.g. "dabelo:a3f9c21b4d2e"
    """
    params = sorted(request.GET.items())
    qs_hash = hashlib.md5(json.dumps(params).encode()).hexdigest()[:12]
    return f"{brand}:{qs_hash}"


def invalidate_shop_cache() -> None:
    """Wipe all shop list page cache entries. Call after any product change."""
    count = _shop_cache.invalidate_namespace()
    logger.info("Shop cache invalidated — %d keys removed", count)


def invalidate_product_cache(slug: str) -> None:
    """Wipe a single product detail cache entry."""
    _product_cache.delete(slug)


def invalidate_all_product_cache() -> None:
    """Wipe all product detail cache entries."""
    count = _product_cache.invalidate_namespace()
    logger.info("Product cache invalidated — %d keys removed", count)


class ProductQueryService:
    @staticmethod
    def base_queryset() -> QuerySet:
        """
        Base queryset for shop list pages.
        Only selects what list cards need — no gallery prefetch here
        since list pages only show the primary image.
        """
        return (
            Product.objects.filter(is_active=True)
            .select_related("category", "primary_image")
            .order_by("-is_featured", "-created_at")
        )

    @staticmethod
    def apply_filters(
        qs: QuerySet,
        request: HttpRequest,
    ) -> tuple[QuerySet, str, str, str, bool]:
        q = request.GET.get("q", "").strip()
        category_slug = request.GET.get("category", "").strip()
        sort = request.GET.get("sort", "").strip()
        in_stock = request.GET.get("in_stock", "") == "1"

        if q:
            qs = qs.filter(name__icontains=q)
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if in_stock:
            qs = qs.filter(in_stock=True)
        if sort == "price_asc":
            qs = qs.order_by("price")
        elif sort == "price_desc":
            qs = qs.order_by("-price")
        elif sort == "newest":
            qs = qs.order_by("-created_at")

        return qs, q, category_slug, sort, in_stock

    @staticmethod
    def paginate(
        qs: QuerySet, request: HttpRequest, per_page: int = PRODUCTS_PER_PAGE
    ) -> tuple:
        from django.core.paginator import Paginator

        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(request.GET.get("page", 1))
        return page_obj, paginator.count

    @staticmethod
    def query_string(request: HttpRequest) -> str:
        """Querystring without page param — for pagination links."""
        params = request.GET.copy()
        params.pop("page", None)
        qs = params.urlencode()
        return f"?{qs}&" if qs else "?"

    @staticmethod
    def serialise_page(page_obj) -> list[dict]:
        """
        Convert a Page of Product instances into a list of plain dicts.
        """
        results = []
        for p in page_obj.object_list:
            results.append(
                {
                    "pk": str(p.pk),
                    "name": p.name,
                    "slug": p.slug,
                    "absolute_url": p.get_absolute_url(),
                    "brand": p.brand,
                    "short_description": p.short_description,
                    "display_price": str(p.display_price) if p.display_price else None,
                    "is_quote_only": p.is_quote_only,
                    "in_stock": p.in_stock,
                    "is_featured": p.is_featured,
                    "product_type": p.product_type,
                    "image_url": p.get_image_url(),
                    "category_name": p.category.name if p.category else None,
                    "category_slug": p.category.slug if p.category else None,
                }
            )
        return results

    @staticmethod
    def serialise_pagination(page_obj) -> dict:
        """Plain dict of pagination state — safe to cache."""
        p = page_obj.paginator
        return {
            "current_page": page_obj.number,
            "num_pages": p.num_pages,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "previous_page": page_obj.previous_page_number()
            if page_obj.has_previous()
            else None,
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
            "page_range": list(p.page_range),
        }

    @staticmethod
    def variations_as_json(product: Product) -> str:
        """
        Serialise variations for the frontend variation switcher.
        """
        data = {}
        for v in product.variations.select_related("image").all():
            data[str(v.pk)] = {
                "name": v.name,
                "price": str(v.price),
                "in_stock": v.in_stock,
                "image": v.get_image_url(),
            }
        return json.dumps(data)

    @staticmethod
    def get_related(product: Product, limit: int = 4) -> list[dict]:
        """
        Products in the same category + brand, excluding current.
        Falls back to same brand only if category yields fewer than 2.
        Returns a list of plain dicts — ready to cache and render.
        """
        base_qs = (
            Product.objects.filter(is_active=True, brand=product.brand)
            .exclude(pk=product.pk)
            .select_related("primary_image", "category")
            .order_by("-is_featured", "-created_at")
        )

        if product.category_id:
            category_results = list(base_qs.filter(category=product.category)[:limit])
            if len(category_results) >= 2:
                return ProductQueryService._serialise_related(category_results)

        return ProductQueryService._serialise_related(list(base_qs[:limit]))

    @staticmethod
    def _serialise_related(products: list) -> list[dict]:
        return [
            {
                "name": p.name,
                "absolute_url": p.get_absolute_url(),
                "image_url": p.get_image_url(),
                "display_price": str(p.display_price) if p.display_price else None,
                "is_quote_only": p.is_quote_only,
                "category_name": p.category.name if p.category else None,
            }
            for p in products
        ]

    @staticmethod
    def build_breadcrumbs(product: Product) -> list[dict]:
        crumbs: list[dict[str, Any]] = [{"label": "Shop", "url": "/shop/"}]
        if product.brand == BrandChoices.DABELO:
            crumbs.append({"label": "Dabelo Café", "url": "/shop/dabelo/"})
        else:
            crumbs.append({"label": "Motee Cakes", "url": "/shop/montee/"})
        if product.category:
            crumbs.append(
                {
                    "label": product.category.name,
                    "url": product.category.get_absolute_url(),
                }
            )
        crumbs.append({"label": product.name, "url": None})
        return crumbs


class QuoteService:
    REQUIRED_FIELDS = ("name", "email", "phone", "description")

    @staticmethod
    def extract_fields(post: dict) -> dict:
        return {
            "name": post.get("name", "").strip(),
            "email": post.get("email", "").strip().lower(),
            "phone": post.get("phone", "").strip(),
            "description": post.get("description", "").strip(),
            "occasion": post.get("occasion", "").strip(),
            "budget": post.get("budget", "").strip(),
            "delivery_date": post.get("delivery_date", "").strip(),
            "brand": post.get("brand", "").strip(),
        }

    @staticmethod
    def validate(fields: dict) -> dict:
        errors = {}
        for f in QuoteService.REQUIRED_FIELDS:
            if not fields.get(f):
                errors[f] = "This field is required."
        if fields.get("email") and "@" not in fields["email"]:
            errors["email"] = "Enter a valid email address."
        return errors

    @staticmethod
    def is_ajax(request: HttpRequest) -> bool:
        return request.headers.get("X-Requested-With") == "XMLHttpRequest"

    @staticmethod
    def create_request(fields: dict, product=None):
        from products.models import CustomOrderRequest

        return CustomOrderRequest.objects.create(
            product=product,
            name=fields["name"],
            email=fields["email"],
            phone=fields["phone"],
            description=fields["description"],
            occasion=fields.get("occasion", ""),
            budget=fields.get("budget", ""),
            delivery_date=fields.get("delivery_date") or None,
            brand=fields.get("brand", ""),
            status="new",
        )
