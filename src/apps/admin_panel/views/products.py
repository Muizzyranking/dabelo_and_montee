from __future__ import annotations

from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.admin_panel.permissions import admin_required
from apps.admin_panel.services import ProductService
from apps.images.services import ImageService
from apps.products.models import (
    Category,
    Product,
    ProductGalleryImage,
    ProductVariation,
)

STATUS_FIELDS = [
    ("is_active", "Active", "Visible in the shop"),
    ("in_stock", "In Stock", "Available to purchase"),
    ("is_featured", "Featured", "Highlighted on shop pages"),
    ("is_quote_only", "Quote Only", "No direct purchase — request a quote"),
]


def _brand_perm(request, brand, mode="view"):
    profile = request.user.admin_profile
    if profile.is_superadmin:
        return True
    return getattr(profile, f"can_{mode}_{brand}_products", False)


@admin_required()
def product_list(request):
    profile = request.user.admin_profile
    brand = request.GET.get("brand", "all")
    search = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")

    qs = Product.objects.select_related("category", "primary_image").order_by(
        "-created_at"
    )

    if not profile.is_superadmin:
        allowed = []
        if profile.can_view_dabelo_products:
            allowed.append("dabelo")
        if profile.can_view_montee_products:
            allowed.append("montee")
        qs = qs.filter(brand__in=allowed)

    if brand != "all":
        qs = qs.filter(brand=brand)
    if search:
        qs = qs.filter(name__icontains=search)
    if category:
        qs = qs.filter(category__slug=category)

    return render(
        request,
        "admin_panel/products/list.html",
        {
            "products": qs,
            "categories": Category.objects.all(),
            "brand": brand,
            "search": search,
            "profile": profile,
        },
    )


@admin_required()
def product_add(request):
    profile = request.user.admin_profile
    categories = Category.objects.all()

    allowed_brands = []
    if profile.is_superadmin or profile.can_edit_dabelo_products:
        allowed_brands.append(("dabelo", "🌿 Dabelo Café"))
    if profile.is_superadmin or profile.can_edit_montee_products:
        allowed_brands.append(("montee", "🎂 Motee Cakes"))

    if request.method == "POST":
        brand = request.POST.get("brand", "")

        if not _brand_perm(request, brand, "edit"):
            messages.error(
                request, "You don't have permission to add products for this brand."
            )
            return redirect("ap_product_list")

        product = Product(
            brand=brand,
            name=request.POST.get("name", "").strip(),
            slug=request.POST.get("slug", "").strip() or None,
            product_type=request.POST.get("product_type", "simple"),
            is_quote_only=request.POST.get("is_quote_only") == "on",
            in_stock=request.POST.get("in_stock") == "on",
            is_featured=request.POST.get("is_featured") == "on",
            is_active=request.POST.get("is_active") == "on",
            short_description=request.POST.get("short_description", "").strip(),
            description=request.POST.get("description", "").strip(),
        )

        cat_id = request.POST.get("category")
        if cat_id:
            product.category_id = cat_id

        if product.product_type == "simple":
            price = request.POST.get("price", "").strip()
            if price:
                product.price = price

        product.save()

        if file := request.FILES.get("primary_image"):
            ProductService.set_primary_image(
                product, file, alt_text=request.POST.get("primary_image_alt", "")
            )
        if files := request.FILES.getlist("gallery_images"):
            ProductService.add_gallery_images(
                product, files, alt_text=request.POST.get("gallery_alt", "")
            )

        ProductService.save_variations(product, request.POST, request.FILES)
        ProductService.save_attributes(product, request.POST)

        messages.success(request, f'"{product.name}" created successfully.')
        return redirect("ap_product_edit", pk=product.pk)

    return render(
        request,
        "admin_panel/products/form.html",
        {
            "mode": "add",
            "categories": categories,
            "allowed_brands": allowed_brands,
            "profile": profile,
            "status_fields": STATUS_FIELDS,
        },
    )


@admin_required()
def product_edit(request, pk):
    product = get_object_or_404(Product.objects.select_related("primary_image"), pk=pk)
    profile = request.user.admin_profile

    if not _brand_perm(request, product.brand, "view"):
        raise Http404

    can_edit = _brand_perm(request, product.brand, "edit")

    if request.method == "POST" and can_edit:
        product.name = request.POST.get("name", "").strip()
        product.slug = request.POST.get("slug", "").strip() or product.slug
        product.product_type = request.POST.get("product_type", "simple")
        product.is_quote_only = request.POST.get("is_quote_only") == "on"
        product.in_stock = request.POST.get("in_stock") == "on"
        product.is_featured = request.POST.get("is_featured") == "on"
        product.is_active = request.POST.get("is_active") == "on"
        product.short_description = request.POST.get("short_description", "").strip()
        product.description = request.POST.get("description", "").strip()

        cat_id = request.POST.get("category")
        product.category_id = cat_id if cat_id else None

        if product.product_type == "simple":
            price = request.POST.get("price", "").strip()
            product.price = price if price else None
        else:
            product.price = None

        product.save()

        if file := request.FILES.get("primary_image"):
            ProductService.set_primary_image(
                product, file, alt_text=request.POST.get("primary_image_alt", "")
            )
        if files := request.FILES.getlist("gallery_images"):
            ProductService.add_gallery_images(
                product, files, alt_text=request.POST.get("gallery_alt", "")
            )

        ProductService.save_variations(product, request.POST, request.FILES)
        ProductService.save_attributes(product, request.POST)

        messages.success(request, f'"{product.name}" updated successfully.')
        return redirect("ap_product_edit", pk=product.pk)

    gallery_entries = product.gallery.select_related("image").all()
    variations = product.variations.select_related("image").order_by("order")
    attributes = product.attributes.all().order_by("order")

    return render(
        request,
        "admin_panel/products/form.html",
        {
            "mode": "edit",
            "product": product,
            "categories": Category.objects.all(),
            "variations": variations,
            "attributes": attributes,
            "gallery_entries": gallery_entries,
            "can_edit": can_edit,
            "profile": profile,
            "status_fields": STATUS_FIELDS,
            "allowed_brands": [
                ("dabelo", "🌿 Dabelo Café"),
                ("montee", "🎂 Motee Cakes"),
            ],
        },
    )


@require_POST
@admin_required()
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not _brand_perm(request, product.brand, "edit"):
        raise Http404

    name = product.name
    ProductService.delete_product(product)
    messages.success(request, f'"{name}" deleted.')
    return redirect("ap_product_list")


@require_POST
@admin_required()
def variation_delete(request, pk):
    variation = get_object_or_404(
        ProductVariation.objects.select_related("image"), pk=pk
    )
    product = variation.product

    if not _brand_perm(request, product.brand, "edit"):
        raise Http404

    if variation.image_id:
        ImageService.delete(variation.image)

    variation.delete()
    return JsonResponse({"ok": True})


@require_POST
@admin_required()
def image_delete(request, pk):
    """Delete a gallery entry — pk is ProductGalleryImage.pk."""
    entry = get_object_or_404(
        ProductGalleryImage.objects.select_related("image"), pk=pk
    )
    product = entry.product

    if not _brand_perm(request, product.brand, "edit"):
        raise Http404

    image = entry.image
    entry.delete()
    ImageService.delete(image)
    return JsonResponse({"ok": True})


@require_POST
@admin_required()
def primary_image_delete(request, pk):
    """Remove and delete the primary image from a product."""
    product = get_object_or_404(Product.objects.select_related("primary_image"), pk=pk)

    if not _brand_perm(request, product.brand, "edit"):
        raise Http404

    if product.primary_image_id:
        old = product.primary_image
        product.primary_image = None
        product.save(update_fields=["primary_image"])
        ImageService.delete(old)

    return JsonResponse({"ok": True})
