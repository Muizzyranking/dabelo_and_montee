from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.admin_panel.permissions import admin_required
from apps.products.models import CustomOrderRequest


@admin_required("can_view_quotes")
def quote_list(request):
    status = request.GET.get("status", "")
    search = request.GET.get("q", "").strip()

    qs = CustomOrderRequest.objects.select_related("product").order_by("-created_at")

    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(name__icontains=search) | qs.filter(email__icontains=search)

    return render(
        request,
        "admin_panel/quotes/list.html",
        {
            "quotes": qs,
            "status_filter": status,
            "search": search,
            "status_choices": CustomOrderRequest.STATUS_CHOICES
            if hasattr(CustomOrderRequest, "STATUS_CHOICES")
            else [],
        },
    )


@admin_required("can_view_quotes")
def quote_detail(request, pk):
    quote = get_object_or_404(CustomOrderRequest, pk=pk)
    can_edit = (
        request.user.admin_profile.is_superadmin
        or request.user.admin_profile.can_edit_quotes
    )

    # Auto-mark as in_review when opened
    if quote.status == "new" and can_edit:
        quote.status = "in_review"
        quote.save()

    return render(
        request,
        "admin_panel/quotes/detail.html",
        {
            "quote": quote,
            "can_edit": can_edit,
            "statuses": [
                ("new", "New"),
                ("in_review", "In Review"),
                ("quoted", "Quoted"),
                ("accepted", "Accepted"),
                ("declined", "Declined"),
            ],
        },
    )


@require_POST
@admin_required("can_edit_quotes")
def quote_update_status(request, pk):
    quote = get_object_or_404(CustomOrderRequest, pk=pk)
    new_status = request.POST.get("status", "")
    quote.status = new_status
    quote.save()

    # sendmail(
    #   to=quote.email,
    #   subject="Update on your custom order request",
    #   body=f"Hi {quote.name}, your quote request status is now: {new_status}."
    # )

    messages.success(request, "Quote status updated.")
    return redirect("ap_quote_detail", pk=pk)
