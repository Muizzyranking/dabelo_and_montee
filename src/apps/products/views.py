from __future__ import annotations

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.rate_limit import limit_submit_general_quote, limit_submit_quote
from core.seo import (
    seo_category,
    seo_custom_order,
    seo_product,
    seo_shop_dabelo,
    seo_shop_joint,
    seo_shop_montee,
)
from core.utils import set_brand

from .models import BrandChoices, Category, Product
from .services import (
    ProductQueryService,
    QuoteService,
    _make_shop_key,
    _product_cache,
    _shop_cache,
)


def _serialise_categories(qs) -> list[dict]:
    """Plain dicts from a Category queryset — safe to cache."""
    return [
        {
            "name": c.name,
            "slug": c.slug,
            "absolute_url": c.get_absolute_url(),
        }
        for c in qs
    ]


def shop_joint(request):
    cache_key = _make_shop_key("joint", request)
    cached = _shop_cache.get(cache_key)

    if cached is None:
        qs = ProductQueryService.base_queryset()
        qs, q, category_slug, sort, in_stock = ProductQueryService.apply_filters(qs, request)

        brand_filter = request.GET.get("brand", "").strip()
        if brand_filter in ("dabelo", "montee"):
            qs = qs.filter(brand=brand_filter)

        page_obj, total_count = ProductQueryService.paginate(qs, request)

        cached = {
            "products": ProductQueryService.serialise_page(page_obj),
            "pagination": ProductQueryService.serialise_pagination(page_obj),
            "categories": _serialise_categories(
                Category.objects.filter(is_active=True).order_by("order", "name")
            ),
            "q": q,
            "category_slug": category_slug,
            "sort": sort,
            "in_stock": in_stock,
            "brand_filter": brand_filter,
            "shop_mode": "joint",
            "page_title": "The Shop",
            "page_subtitle": "Dabelo Café & Motee Cakes — everything in one place.",
            "result_count": total_count,
            "query_string": ProductQueryService.query_string(request),
            "seo": seo_shop_joint(),
        }
        _shop_cache.set(cache_key, cached)

    return render(request, "shop/joint.html", cached)


def shop_dabelo(request):
    cache_key = _make_shop_key("dabelo", request)
    cached = _shop_cache.get(cache_key)

    if cached is None:
        qs = ProductQueryService.base_queryset().filter(brand=BrandChoices.DABELO)
        qs, q, category_slug, sort, in_stock = ProductQueryService.apply_filters(qs, request)
        page_obj, total_count = ProductQueryService.paginate(qs, request)

        cached = {
            "products": ProductQueryService.serialise_page(page_obj),
            "pagination": ProductQueryService.serialise_pagination(page_obj),
            "categories": _serialise_categories(
                Category.objects.filter(is_active=True, brand=BrandChoices.DABELO).order_by(
                    "order", "name"
                )
            ),
            "q": q,
            "category_slug": category_slug,
            "sort": sort,
            "in_stock": in_stock,
            "result_count": total_count,
            "query_string": ProductQueryService.query_string(request),
            # Layout / copy
            "base_template": "dabelo/base.html",
            "brand_class": "shop-dabelo",
            "action_url": reverse("shop_dabelo"),
            "clear_url": reverse("shop_dabelo"),
            "back_url": reverse("dabelo_home"),
            "cross_brand_url": reverse("shop_montee"),
            "page_title": "Dabelo Café",
            "page_subtitle": "Cold-pressed juices, fresh bowls & healthy meal prep.",
            "watermark": "Dabelo",
            "hero_eyebrow": "Dabelo Café · Lagos",
            "hero_title": "Fresh. <em>Natural.</em> Delivered.",
            "back_label": "← Back to Dabelo",
            "cross_brand_label": "🎂 Montee Cakes",
            "search_placeholder": "Search Dabelo products…",
            "result_label": "product",
            "stock_label": "In Stock Only",
            "available_chip_label": "In Stock",
            "empty_icon": "🌿",
            "empty_title": "Nothing fresh here yet",
            "empty_body": "Try different filters or check back soon.",
            "seo": seo_shop_dabelo(),
        }
        _shop_cache.set(cache_key, cached)

    request = set_brand(request, "dabelo")
    return render(request, "shop/brand.html", cached)


def shop_montee(request):
    cache_key = _make_shop_key("montee", request)
    cached = _shop_cache.get(cache_key)

    if cached is None:
        qs = ProductQueryService.base_queryset().filter(brand=BrandChoices.MONTEE)
        qs, q, category_slug, sort, in_stock = ProductQueryService.apply_filters(qs, request)
        page_obj, total_count = ProductQueryService.paginate(qs, request)

        cached = {
            "products": ProductQueryService.serialise_page(page_obj),
            "pagination": ProductQueryService.serialise_pagination(page_obj),
            "categories": _serialise_categories(
                Category.objects.filter(is_active=True, brand=BrandChoices.MONTEE).order_by(
                    "order", "name"
                )
            ),
            "q": q,
            "category_slug": category_slug,
            "sort": sort,
            "in_stock": in_stock,
            "result_count": total_count,
            "query_string": ProductQueryService.query_string(request),
            # Layout / copy
            "base_template": "montee/base.html",
            "brand_class": "shop-montee",
            "action_url": reverse("shop_montee"),
            "clear_url": reverse("shop_montee"),
            "back_url": reverse("montee_home"),
            "cross_brand_url": reverse("shop_dabelo"),
            "page_title": "Motee Cakes",
            "page_subtitle": "Bespoke handcrafted cakes for every celebration.",
            "watermark": "Motee",
            "hero_eyebrow": "Motee Cakes · Lagos",
            "hero_title": "Cakes Made <em>Unforgettable.</em>",
            "back_label": "← Back to Motee",
            "cross_brand_label": "🌿 Dabelo Café",
            "search_placeholder": "Search cakes…",
            "result_label": "cake",
            "stock_label": "Available Only",
            "available_chip_label": "Available",
            "empty_icon": "🎂",
            "empty_title": "No cakes found",
            "empty_body": "Try adjusting your filters.",
            "seo": seo_shop_montee(),
        }
        _shop_cache.set(cache_key, cached)

    request = set_brand(request, "montee")
    return render(request, "shop/brand.html", cached)


def shop_category(request, slug):
    cache_key = _make_shop_key(f"category:{slug}", request)
    cached = _shop_cache.get(cache_key)

    if cached is None:
        category = get_object_or_404(Category, slug=slug, is_active=True)
        qs = ProductQueryService.base_queryset().filter(category=category)
        qs, q, category_slug, sort, in_stock = ProductQueryService.apply_filters(qs, request)
        page_obj, total_count = ProductQueryService.paginate(qs, request)

        cached = {
            "products": ProductQueryService.serialise_page(page_obj),
            "pagination": ProductQueryService.serialise_pagination(page_obj),
            "categories": _serialise_categories(
                Category.objects.filter(is_active=True, brand=category.brand).order_by(
                    "order", "name"
                )
            ),
            "current_category": {"name": category.name, "slug": category.slug},
            "q": q,
            "category_slug": category.slug,
            "sort": sort,
            "in_stock": in_stock,
            "shop_mode": category.brand,
            "page_title": category.name,
            "page_subtitle": category.description or f"Browse our {category.name} collection.",
            "result_count": total_count,
            "query_string": ProductQueryService.query_string(request),
            "seo": seo_category(category),
        }
        _shop_cache.set(cache_key, cached)

    return render(request, "shop/category.html", cached)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.filter(is_active=True)
        .select_related("category", "primary_image")
        .prefetch_related("gallery__image", "variations__image", "attributes"),
        slug=slug,
    )

    cached = _product_cache.get(slug)
    if cached is None:
        cached = {
            "primary_image_url": product.get_image_url(),
            "gallery": product.get_gallery_images(),
            "variations_data": ProductQueryService.variations_as_json(product),
            "breadcrumbs": ProductQueryService.build_breadcrumbs(product),
            "related": ProductQueryService.get_related(product),
            "seo": seo_product(product),
        }
        _product_cache.set(slug, cached)

    base_template = (
        "dabelo/base.html" if product.brand == BrandChoices.DABELO else "montee/base.html"
    )
    request = set_brand(
        request,
        "dabelo" if product.brand == BrandChoices.DABELO else "montee",
    )

    context = {
        # Fresh model data — never cached
        "product": product,
        "variations": product.variations.all(),
        "attributes": product.attributes.all(),
        "base_template": base_template,
        "brand": product.brand,
        "quote_url": reverse("submit_quote", kwargs={"slug": product.slug}),
        # Cached plain data
        **cached,
    }

    return render(request, "shop/product_detail.html", context)


@limit_submit_quote
@require_POST
def submit_quote(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    fields = QuoteService.extract_fields(request.POST)
    errors = QuoteService.validate(fields)
    is_ajax = QuoteService.is_ajax(request)

    if errors:
        if is_ajax:
            return JsonResponse({"ok": False, "errors": errors}, status=400)
        messages.error(request, "Please fill all required fields.")
        return redirect("product_detail", slug=slug)

    QuoteService.create_request(fields, product=product)

    if is_ajax:
        return JsonResponse({"ok": True})
    messages.success(request, "Quote sent! We'll be in touch shortly.")
    return redirect("product_detail", slug=slug)


@limit_submit_general_quote
@require_POST
def submit_general_quote(request):
    fields = QuoteService.extract_fields(request.POST)
    errors = QuoteService.validate(fields)
    is_ajax = QuoteService.is_ajax(request)

    if errors:
        if is_ajax:
            return JsonResponse({"ok": False, "errors": errors}, status=400)
        messages.error(request, "Please fill in all required fields.")
        return redirect("custom_order")

    QuoteService.create_request(fields, product=None)

    if is_ajax:
        return JsonResponse({"ok": True})
    messages.success(request, "Quote sent! We'll be in touch within 24 hours.")
    return redirect("custom_order")


def custom_order_page(request):
    steps = [
        {
            "icon": "✉️",
            "title": "Send Your Request",
            "body": "Fill out the form with what you need — as much detail as possible helps us respond faster.",
        },
        {
            "icon": "💬",
            "title": "We Get Back to You",
            "body": "Our team reviews your request and reaches out within 24 hours with options and pricing.",
        },
        {
            "icon": "🎉",
            "title": "We Make It Happen",
            "body": "Once agreed, we get to work. Your order is prepared fresh and delivered on time.",
        },
    ]
    return render(
        request,
        "shop/custom_order.html",
        {
            "steps": steps,
            "seo": seo_custom_order(),
        },
    )
