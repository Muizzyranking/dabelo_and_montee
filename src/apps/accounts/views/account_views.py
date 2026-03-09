from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.products.models import CustomOrderRequest, Order

User = get_user_model()


@login_required(login_url="/auth/")
def dashboard(request):
    user = request.user
    recent_orders = Order.objects.filter(user=user).order_by("-created_at")[:3]
    recent_quotes = CustomOrderRequest.objects.filter(email=user.email).order_by(
        "-created_at"
    )[:3]
    order_count = Order.objects.filter(user=user).count()
    quote_count = CustomOrderRequest.objects.filter(email=user.email).count()
    hour = datetime.now().hour
    greeting = (
        "Good morning"
        if hour < 12
        else "Good afternoon"
        if hour < 17
        else "Good evening"
    )
    context = {
        "recent_orders": recent_orders,
        "recent_quotes": recent_quotes,
        "order_count": order_count,
        "quote_count": quote_count,
        "greeting": greeting,
    }

    return render(request, "accounts/dashboard.html", context)


@login_required(login_url="/auth/")
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "accounts/orders.html", {"orders": orders})


@login_required(login_url="/auth/")
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, "accounts/order_detail.html", {"order": order})


@login_required(login_url="/auth/")
def quote_list(request):
    quotes = CustomOrderRequest.objects.filter(email=request.user.email).order_by(
        "-created_at"
    )
    return render(request, "accounts/quotes.html", {"quotes": quotes})


@login_required(login_url="/auth/")
def profile(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.phone = request.POST.get("phone", "").strip()

        new_email = request.POST.get("email", "").strip().lower()
        if new_email != user.email:
            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                messages.error(request, "That email is already in use.")
                return redirect("account_profile")
            user.email = new_email

        user.marketing_emails = request.POST.get("marketing_emails") == "on"
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("account_profile")

    return render(request, "accounts/profile.html")


@login_required(login_url="/auth/")
def address(request):
    if request.method == "POST":
        user = request.user
        user.address_line_1 = request.POST.get("address_line_1", "").strip()
        user.address_line_2 = request.POST.get("address_line_2", "").strip()
        user.city = request.POST.get("city", "").strip()
        user.state = request.POST.get("state", "").strip()
        user.save()
        messages.success(request, "Address saved successfully.")
        return redirect("account_address")

    return render(request, "accounts/address.html")


@login_required(login_url="/auth/")
def change_password(request):
    if request.method == "POST":
        current = request.POST.get("current_password", "")
        new_pw = request.POST.get("new_password", "")
        confirm = request.POST.get("confirm_password", "")

        if not request.user.check_password(current):
            messages.error(request, "Current password is incorrect.")
            return redirect("account_password")
        if len(new_pw) < 8:
            messages.error(request, "New password must be at least 8 characters.")
            return redirect("account_password")
        if new_pw != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("account_password")

        request.user.set_password(new_pw)
        request.user.save()
        update_session_auth_hash(request, request.user)  # keep them logged in
        messages.success(request, "Password changed successfully.")
        return redirect("account_password")

    return render(request, "accounts/change_password.html")
