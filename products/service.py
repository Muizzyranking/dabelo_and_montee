import json
from typing import Any

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

from .models import BrandChoices, CustomOrderRequest, Product

PRODUCTS_PER_PAGE = 3


class ProductQueryService:
    @classmethod
    def base_queryset(cls):
        return (
            Product.objects.filter(is_active=True)
            .prefetch_related("images", "variations", "attributes")
            .select_related("category")
            .order_by("-created_at")
        )

    @classmethod
    def apply_filters(cls, qs, request):
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

        sort_map = {
            "price_asc": "price",
            "price_desc": "-price",
            "featured": ("-is_featured", "-created_at"),
        }
        order = sort_map.get(sort, "-created_at")
        qs = qs.order_by(*order) if isinstance(order, tuple) else qs.order_by(order)

        return qs, q, category_slug, sort, in_stock

    @classmethod
    def paginate(cls, qs, request):
        paginator = Paginator(qs, PRODUCTS_PER_PAGE)
        page_num = request.GET.get("page", 1)
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj, paginator.count

    @classmethod
    def query_string(cls, request, exclude=("page",)):
        params = request.GET.copy()
        for key in exclude:
            params.pop(key, None)
        qs = params.urlencode()
        return f"?{qs}&" if qs else "?"

    @classmethod
    def get_related(cls, product, limit=4):
        if not product.category:
            return []
        return (
            Product.objects.filter(is_active=True, category=product.category)
            .exclude(pk=product.pk)
            .prefetch_related("images")
            .order_by("-is_featured", "-created_at")[:limit]
        )

    @classmethod
    def variations_as_json(cls, product):
        data = [
            {
                "id": str(v.id),
                "name": v.name,
                "price": float(v.price) if v.price else None,
                "in_stock": v.in_stock,
                "image": v.image.url if v.image else None,
            }
            for v in product.variations.all()
        ]
        return json.dumps(data)

    @classmethod
    def build_breadcrumbs(cls, product) -> list[dict[str, Any]]:
        crumbs: list[dict[str, Any]] = [{"label": "Shop", "url": "/shop/"}]

        if product.brand == BrandChoices.DABELO:
            crumbs.append({"label": "Dabelo Café", "url": "/shop/dabelo/"})
        else:
            crumbs.append({"label": "Motee Cakes", "url": "/shop/montee/"})

        if product.category:
            crumbs.append(
                {
                    "label": product.category.name,
                    "url": f"/shop/category/{product.category.slug}/",
                }
            )

        crumbs.append({"label": product.name, "url": None})
        return crumbs


class QuoteService:
    @classmethod
    def extract_fields(cls, post):
        return {
            "name": post.get("name", "").strip(),
            "email": post.get("email", "").strip(),
            "phone": post.get("phone", "").strip(),
            "description": post.get("description", "").strip(),
            "occasion": post.get("occasion", "").strip(),
            "budget": post.get("budget", "").strip(),
            "delivery_date": post.get("delivery_date") or None,
        }

    @classmethod
    def validate(cls, fields) -> dict[str, str]:
        errors: dict[str, str] = {}
        required = {
            "name": "Name is required.",
            "email": "Email is required.",
            "phone": "Phone number is required.",
            "description": "Please describe what you need.",
        }
        for field, message in required.items():
            if not fields.get(field):
                errors[field] = message
        return errors

    @classmethod
    def create_request(cls, fields, product=None):
        return CustomOrderRequest.objects.create(
            product=product,
            name=fields["name"],
            email=fields["email"],
            phone=fields["phone"],
            occasion=fields["occasion"],
            description=fields["description"],
            budget=fields["budget"],
            delivery_date=fields["delivery_date"],
        )

    @classmethod
    def is_ajax(cls, request):
        return request.headers.get("X-Requested-With") == "XMLHttpRequest"
