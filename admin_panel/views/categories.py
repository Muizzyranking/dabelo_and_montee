from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from admin_panel.permissions import admin_required
from products.models import Category


def _brand_perm(request, brand, mode="view"):
    profile = request.user.admin_profile
    if profile.is_superadmin:
        return True
    perm = f"can_{mode}_{brand}_products"
    return getattr(profile, perm, False)


@admin_required()
def category_list(request):
    profile = request.user.admin_profile
    brand = request.GET.get("brand", "all")

    qs = Category.objects.all()

    if not profile.is_superadmin:
        allowed = []
        if profile.can_view_dabelo_products:
            allowed.append("dabelo")
        if profile.can_view_montee_products:
            allowed.append("montee")
        qs = qs.filter(brand__in=allowed)

    if brand != "all":
        qs = qs.filter(brand=brand)

    return render(
        request,
        "admin_panel/categories/list.html",
        {
            "categories": qs,
            "brand": brand,
            "profile": profile,
        },
    )


@admin_required()
def category_add(request):
    profile = request.user.admin_profile

    allowed_brands = []
    if profile.is_superadmin or profile.can_edit_dabelo_products:
        allowed_brands.append(("dabelo", "🌿 Dabelo Café"))
    if profile.is_superadmin or profile.can_edit_montee_products:
        allowed_brands.append(("montee", "🎂 Motee Cakes"))

    if request.method == "POST":
        brand = request.POST.get("brand", "")

        if not _brand_perm(request, brand, "edit"):
            messages.error(
                request, "You don't have permission to add categories for this brand."
            )
            return redirect("ap_category_list")

        name = request.POST.get("name", "").strip()
        slug = request.POST.get("slug", "").strip() or slugify(name)
        description = request.POST.get("description", "").strip()
        order = request.POST.get("order", 0) or 0
        is_active = request.POST.get("is_active") == "on"

        if not name:
            messages.error(request, "Category name is required.")
            return render(
                request,
                "admin_panel/categories/form.html",
                {
                    "mode": "add",
                    "allowed_brands": allowed_brands,
                    "profile": profile,
                },
            )

        if Category.objects.filter(slug=slug).exists():
            slug = f"{slug}-2"

        category = Category(
            brand=brand,
            name=name,
            slug=slug,
            description=description,
            order=int(order),
            is_active=is_active,
        )

        img = request.FILES.get("image")
        if img:
            category.image = img

        category.save()

        messages.success(request, f'Category "{name}" created.')
        return redirect("ap_category_list")

    return render(
        request,
        "admin_panel/categories/form.html",
        {
            "mode": "add",
            "allowed_brands": allowed_brands,
            "profile": profile,
        },
    )


@admin_required()
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    profile = request.user.admin_profile

    if not _brand_perm(request, category.brand, "view"):
        from django.http import Http404

        raise Http404

    can_edit = _brand_perm(request, category.brand, "edit")

    allowed_brands = [
        ("dabelo", "🌿 Dabelo Café"),
        ("montee", "🎂 Motee Cakes"),
    ]

    if request.method == "POST" and can_edit:
        category.name = request.POST.get("name", "").strip()
        category.description = request.POST.get("description", "").strip()
        category.order = int(request.POST.get("order", 0) or 0)
        category.is_active = request.POST.get("is_active") == "on"

        new_slug = request.POST.get("slug", "").strip()
        if new_slug and new_slug != category.slug:
            category.slug = new_slug

        img = request.FILES.get("image")
        if img:
            category.image = img

        # Clear image if requested
        if request.POST.get("clear_image") == "on":
            category.image = None

        category.save()
        messages.success(request, f'Category "{category.name}" updated.')
        return redirect("ap_category_list")

    product_count = category.products.filter(is_active=True).count()

    return render(
        request,
        "admin_panel/categories/form.html",
        {
            "mode": "edit",
            "category": category,
            "allowed_brands": allowed_brands,
            "can_edit": can_edit,
            "profile": profile,
            "product_count": product_count,
        },
    )


@require_POST
@admin_required()
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if not _brand_perm(request, category.brand, "edit"):
        from django.http import Http404

        raise Http404

    product_count = category.products.count()
    if product_count > 0:
        messages.error(
            request,
            f'Cannot delete "{category.name}" — it has {product_count} product(s). '
            f"Reassign or delete those products first.",
        )
        return redirect("ap_category_list")

    name = category.name
    category.delete()
    messages.success(request, f'Category "{name}" deleted.')
    return redirect("ap_category_list")
