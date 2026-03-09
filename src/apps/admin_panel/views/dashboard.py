from datetime import timedelta

from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from apps.admin_panel.permissions import admin_required
from apps.products.models import CustomOrderRequest, Order, Product


@admin_required()
def dashboard(request):
    profile = request.user.admin_profile
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    _ = now - timedelta(days=7)

    orders_qs = Order.objects.all()
    total_orders = orders_qs.count()
    orders_this_month = orders_qs.filter(created_at__gte=month_start).count()
    pending_orders = orders_qs.filter(status=Order.Status.PENDING).count()

    total_revenue = orders_qs.filter(is_paid=True).aggregate(t=Sum("total"))["t"] or 0
    revenue_this_month = (
        orders_qs.filter(is_paid=True, created_at__gte=month_start).aggregate(
            t=Sum("total")
        )["t"]
        or 0
    )

    new_quotes = CustomOrderRequest.objects.filter(status="new").count()

    dabelo_count = Product.objects.filter(brand="dabelo", is_active=True).count()
    montee_count = Product.objects.filter(brand="montee", is_active=True).count()

    chart_labels = []
    chart_values = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        rev = (
            orders_qs.filter(
                is_paid=True, paid_at__gte=start, paid_at__lt=end
            ).aggregate(t=Sum("total"))["t"]
            or 0
        )
        chart_labels.append(day.strftime("%b %d"))
        chart_values.append(float(rev))

    recent_orders = orders_qs.order_by("-created_at")[:8]

    context = {
        "profile": profile,
        "total_orders": total_orders,
        "orders_this_month": orders_this_month,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
        "revenue_this_month": revenue_this_month,
        "new_quotes": new_quotes,
        "dabelo_count": dabelo_count,
        "montee_count": montee_count,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "recent_orders": recent_orders,
    }
    return render(request, "admin_panel/dashboard.html", context)
