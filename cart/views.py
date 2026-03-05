from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product, ProductVariation
from . import service as cart_service


def cart_page(request):
    cart = cart_service.get_or_create_cart(request)
    items = cart.items.select_related(
        "product", "product__category", "variation"
    ).prefetch_related("product__images")

    return render(
        request,
        "cart/page.html",
        {
            "cart": cart,
            "items": items,
            "subtotal": cart.subtotal,
        },
    )


def cart_drawer(request):
    """Returns HTML partial for the drawer — called via AJAX."""
    cart = cart_service.get_or_create_cart(request)
    items = cart.items.select_related("product", "variation").prefetch_related(
        "product__images"
    )

    return render(
        request,
        "cart/partials/drawer.html",
        {
            "cart": cart,
            "items": items,
            "subtotal": cart.subtotal,
        },
    )


def cart_count(request):
    """Returns cart item count as JSON — for navbar/floating button updates."""
    cart = cart_service.get_or_create_cart(request)
    return JsonResponse({"count": cart.total_items})


@require_POST
def add_to_cart(request):
    product_id = request.POST.get("product_id")
    variation_id = request.POST.get("variation_id")
    quantity = int(request.POST.get("quantity", 1))

    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if not product.in_stock:
        return JsonResponse(
            {"ok": False, "message": "This product is currently unavailable."},
            status=400,
        )

    variation = None
    if variation_id:
        variation = get_object_or_404(
            ProductVariation, pk=variation_id, product=product
        )
        if not variation.in_stock:
            return JsonResponse(
                {"ok": False, "message": "This variation is currently unavailable."},
                status=400,
            )

    cart, item, created = cart_service.add_item(request, product, variation, quantity)

    name = product.name
    if variation:
        name += f" ({variation.name})"

    return JsonResponse(
        {
            "ok": True,
            "message": f"{name} added to cart.",
            "cart_count": cart.total_items,
            "item_count": item.quantity,
        }
    )


@require_POST
def update_cart(request):
    item_id = request.POST.get("item_id")
    quantity = int(request.POST.get("quantity", 0))

    cart, item = cart_service.update_quantity(request, item_id, quantity)

    return JsonResponse(
        {
            "ok": True,
            "cart_count": cart.total_items,
            "subtotal": str(cart.subtotal),
            "removed": item is None,
        }
    )


@require_POST
def remove_from_cart(request):
    item_id = request.POST.get("item_id")
    cart = cart_service.remove_item(request, item_id)

    return JsonResponse(
        {
            "ok": True,
            "cart_count": cart.total_items,
            "subtotal": str(cart.subtotal),
        }
    )
