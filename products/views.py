from typing import Any
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.utils import set_brand
from .models import Product, Category, BrandChoices
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
def _base_queryset():
    return (
        Product.objects.filter(is_active=True)
        .prefetch_related("images", "variations", "attributes")
        .select_related("category")
        .order_by("-created_at")
    )


def _apply_filters(qs, request):
    q = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "newest")
    in_stock = request.GET.get("in_stock", "")

    if q:
        qs = qs.filter(
            Q(name__icontains=q)
            | Q(short_description__icontains=q)
            | Q(description__icontains=q)
        )

    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    if in_stock == "1":
        qs = qs.filter(in_stock=True)

    if sort == "price_asc":
        qs = qs.order_by("price")
    elif sort == "price_desc":
        qs = qs.order_by("-price")
    elif sort == "featured":
        qs = qs.order_by("-is_featured", "-created_at")
    else:
        qs = qs.order_by("-created_at")

    return qs, q, category_slug, sort, in_stock


def _paginate(qs, request):
    """
    Paginate a queryset.
    """
    paginator = Paginator(qs, PRODUCTS_PER_PAGE)
    page_num = request.GET.get("page", 1)

    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj, paginator.count


def _query_string(request, exclude=("page",)):
    """
    Rebuild the current query string, dropping keys in `exclude`.
    Used so pagination links preserve all active filters.
    """
    params = request.GET.copy()
    for key in exclude:
        params.pop(key, None)
    qs = params.urlencode()
    return f"?{qs}&" if qs else "?"


def shop_joint(request):
    qs = _base_queryset()
    qs, q, category_slug, sort, in_stock = _apply_filters(qs, request)

    brand_filter = request.GET.get("brand", "").strip()
    if brand_filter in ("dabelo", "montee"):
        qs = qs.filter(brand=brand_filter)

    page_obj, total_count = _paginate(qs, request)
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
        "query_string": _query_string(request),
    }
    return render(request, "shop/joint.html", context)


def shop_dabelo(request):
    qs = _base_queryset().filter(brand=BrandChoices.DABELO)
    qs, q, category_slug, sort, in_stock = _apply_filters(qs, request)
    page_obj, total_count = _paginate(qs, request)
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
        "query_string": _query_string(request),
        # — template wiring —
        "base_template": "dabelo/base.html",
        "brand_class": "shop-dabelo",
        "action_url": reverse("shop_dabelo"),
        "clear_url": reverse("shop_dabelo"),
        "back_url": reverse("dabelo_home"),
        "cross_brand_url": reverse("shop_montee"),
        # — copy —
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
    qs = _base_queryset().filter(brand=BrandChoices.MONTEE)
    qs, q, category_slug, sort, in_stock = _apply_filters(qs, request)
    page_obj, total_count = _paginate(qs, request)
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
        "query_string": _query_string(request),
        # — template wiring —
        "base_template": "montee/base.html",
        "brand_class": "shop-montee",
        "action_url": reverse("shop_montee"),
        "clear_url": reverse("shop_montee"),
        "back_url": reverse("montee_home"),
        "cross_brand_url": reverse("shop_dabelo"),
        # — copy —
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
        "result_count": total_count,
        "query_string": _query_string(request),
    }
    request = set_brand(request, "montee")
    return render(request, "shop/montee.html", context)

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.filter(is_active=True)
        .prefetch_related("images", "variations", "attributes")
        .select_related("category"),
        slug=slug,
    )

    # Related — same category, exclude self, max 4
    related = []
    if product.category:
        related = (
            Product.objects.filter(is_active=True, category=product.category)
            .exclude(pk=product.pk)
            .prefetch_related("images")
            .order_by("-is_featured", "-created_at")[:4]
        )

    # Variation data for JS
    variations_data = [
        {
            "id": str(v.id),
            "name": v.name,
            "price": float(v.price) if v.price else None,
            "in_stock": v.in_stock,
            "image": v.image.url if v.image else None,
        }
        for v in product.variations.all()
    ]

    breadcrumbs: list[dict[str, Any]] = [{"label": "Shop", "url": "/shop/"}]
    if product.brand == BrandChoices.DABELO:
        breadcrumbs.append({"label": "Dabelo Café", "url": "/shop/dabelo/"})
    else:
        breadcrumbs.append({"label": "Motee Cakes", "url": "/shop/montee/"})
    if product.category:
        breadcrumbs.append(
            {
                "label": product.category.name,
                "url": f"/shop/category/{product.category.slug}/",
            }
        )
    breadcrumbs.append({"label": product.name, "url": None})

    base_template = (
        "dabelo/base.html"
        if product.brand == BrandChoices.DABELO
        else "montee/base.html"
    )

    context = {
        "product": product,
        "images": product.images.all().order_by("order", "-is_primary"),
        "variations": product.variations.all(),
        "variations_data": variations_data,
        "attributes": product.attributes.all(),
        "related": related,
        "breadcrumbs": breadcrumbs,
        "base_template": base_template,
        "brand": product.brand,
    }
    if product.brand == BrandChoices.DABELO:
        request = set_brand(request, "dabelo")
    else:
        request = set_brand(request, "montee")
    return render(request, "shop/product_detail.html", context)

