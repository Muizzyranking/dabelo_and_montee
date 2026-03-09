from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.admin_panel.permissions import admin_required
from apps.products.models import Order


@admin_required("can_view_orders")
def order_list(request):
    status = request.GET.get("status", "")
    search = request.GET.get("q", "").strip()

    qs = Order.objects.select_related("user").order_by("-created_at")

    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(order_number__icontains=search) | qs.filter(
            delivery_name__icontains=search
        )

    return render(
        request,
        "admin_panel/orders/list.html",
        {
            "orders": qs,
            "status_filter": status,
            "search": search,
            "status_choices": Order.Status.choices,
        },
    )


@admin_required("can_view_orders")
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    items = order.items.select_related("product")

    return render(
        request,
        "admin_panel/orders/detail.html",
        {
            "order": order,
            "items": items,
            "status_choices": Order.Status.choices,
            "can_edit": request.user.admin_profile.is_superadmin
            or request.user.admin_profile.can_edit_orders,
        },
    )


@require_POST
@admin_required("can_edit_orders")
def order_update_status(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    new_status = request.POST.get("status", "")

    valid = [s[0] for s in Order.Status.choices]
    if new_status not in valid:
        messages.error(request, "Invalid status.")
        return redirect("ap_order_detail", order_number=order_number)

    order.status = new_status
    order.save()

    # sendmail(
    #   to=order.user.email,
    #   subject=f"Order {order.order_number} Update",
    #   body=f"Your order status has changed from {old_status} to {new_status}."
    # )

    messages.success(
        request,
        f"Order {order.order_number} status updated to {order.get_status_display()}.",
    )
    return redirect("ap_order_detail", order_number=order_number)
