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
        "shop_mode": "dabelo",
        "page_title": "Dabelo Café",
        "page_subtitle": "Cold-pressed juices, fresh bowls & healthy meal prep.",
        "result_count": total_count,
        "query_string": _query_string(request),
        "watermark": "Dabelo",
    }
    request = set_brand(request, "dabelo")
    return render(request, "shop/dabelo.html", context)


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
        "shop_mode": "montee",
        "page_title": "Motee Cakes",
        "page_subtitle": "Bespoke handcrafted cakes for every celebration.",
        "result_count": total_count,
        "query_string": _query_string(request),
    }
    request = set_brand(request, "montee")
    return render(request, "shop/montee.html", context)
