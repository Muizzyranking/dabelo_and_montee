from typing import Any

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.utils import set_brand

from .models import BrandChoices, Category, Product
from .service import ProductQueryService, QuoteService


def shop_joint(request):
    qs = ProductQueryService.base_queryset()
    qs, q, category_slug, sort, in_stock = ProductQueryService.apply_filters(
        qs, request
    )

    brand_filter = request.GET.get("brand", "").strip()
    if brand_filter in ("dabelo", "montee"):
        qs = qs.filter(brand=brand_filter)

    page_obj, total_count = ProductQueryService.paginate(qs, request)
    categories = Category.objects.filter(is_active=True).order_by("order", "name")

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "paginator": page_obj.paginator,
        "categories": categories,
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
    }
    return render(request, "shop/joint.html", context)


def shop_dabelo(request):
    qs = ProductQueryService.base_queryset().filter(brand=BrandChoices.DABELO)
    qs, q, category_slug, sort, in_stock = ProductQueryService.apply_filters(
        qs, request
    )
    page_obj, total_count = ProductQueryService.paginate(qs, request)
    categories = Category.objects.filter(
        is_active=True, brand=BrandChoices.DABELO
    ).order_by("order", "name")

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "paginator": page_obj.paginator,
        "categories": categories,
        "q": q,
        "category_slug": category_slug,
        "sort": sort,
        "in_stock": in_stock,
        "result_count": total_count,
        "query_string": ProductQueryService.query_string(request),
        # template wiring
        "base_template": "dabelo/base.html",
        "brand_class": "shop-dabelo",
        "action_url": reverse("shop_dabelo"),
        "clear_url": reverse("shop_dabelo"),
        "back_url": reverse("dabelo_home"),
        "cross_brand_url": reverse("shop_montee"),
        # copy
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
        "empty_body": "Try different filters or check back soon — new products are added daily.",
    }
    request = set_brand(request, "dabelo")
    return render(request, "shop/brand.html", context)


def shop_montee(request):
    qs = ProductQueryService.base_queryset().filter(brand=BrandChoices.MONTEE)
    qs, q, category_slug, sort, in_stock = ProductQueryService.apply_filters(
        qs, request
    )
    page_obj, total_count = ProductQueryService.paginate(qs, request)
    categories = Category.objects.filter(
        is_active=True, brand=BrandChoices.MONTEE
    ).order_by("order", "name")

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "paginator": page_obj.paginator,
        "categories": categories,
        "q": q,
        "category_slug": category_slug,
        "sort": sort,
        "in_stock": in_stock,
        "result_count": total_count,
        "query_string": ProductQueryService.query_string(request),
        # template wiring
        "base_template": "montee/base.html",
        "brand_class": "shop-montee",
        "action_url": reverse("shop_montee"),
        "clear_url": reverse("shop_montee"),
        "back_url": reverse("montee_home"),
        "cross_brand_url": reverse("shop_dabelo"),
        # copy
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
        "empty_body": "Try adjusting your filters. We're always adding new creations.",
    }
    request = set_brand(request, "montee")
    return render(request, "shop/brand.html", context)


def shop_category(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)

    qs = ProductQueryService.base_queryset().filter(category=category)
    qs, q, category_slug, sort, in_stock = ProductQueryService.apply_filters(
        qs, request
    )
    page_obj, total_count = ProductQueryService.paginate(qs, request)

    sibling_categories = Category.objects.filter(
        is_active=True, brand=category.brand
    ).order_by("order", "name")

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "paginator": page_obj.paginator,
        "categories": sibling_categories,
        "current_category": category,
        "q": q,
        "category_slug": category.slug,
        "sort": sort,
        "in_stock": in_stock,
        "shop_mode": category.brand,
        "page_title": category.name,
        "page_subtitle": category.description
        or f"Browse our {category.name} collection.",
        "result_count": total_count,
        "query_string": ProductQueryService.query_string(request),
    }
    return render(request, "shop/category.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.filter(is_active=True)
        .prefetch_related("images", "variations", "attributes")
        .select_related("category"),
        slug=slug,
    )

    base_template = (
        "dabelo/base.html"
        if product.brand == BrandChoices.DABELO
        else "montee/base.html"
    )

    context = {
        "product": product,
        "images": product.images.all().order_by("order", "-is_primary"),
        "variations": product.variations.all(),
        "variations_data": ProductQueryService.variations_as_json(product),
        "attributes": product.attributes.all(),
        "related": ProductQueryService.get_related(product),
        "breadcrumbs": ProductQueryService.build_breadcrumbs(product),
        "base_template": base_template,
        "brand": product.brand,
        "quote_url": reverse("submit_quote", kwargs={"slug": product.slug}),
    }

    brand_slug = "dabelo" if product.brand == BrandChoices.DABELO else "montee"
    request = set_brand(request, brand_slug)
    return render(request, "shop/product_detail.html", context)


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
