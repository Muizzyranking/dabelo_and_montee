from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

from cart.service import merge_carts

User = get_user_model()


def auth_page(request):
    """Single page for login + register, toggled by ?tab=register"""
    if request.user.is_authenticated:
        return redirect(_next_or_home(request))

    tab = request.GET.get("tab", "login")
    return render(
        request,
        "accounts/auth_page.html",
        {"tab": tab, "next": request.GET.get("next", "")},
    )


@require_POST
def login_view(request):
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    next_url = request.POST.get("next", "").strip()

    user = authenticate(request, username=email, password=password)

    if user is None:
        messages.error(request, "Invalid email or password. Please try again.")
        url = "/auth/?tab=login"
        if next_url:
            url += f"&next={next_url}"
        return redirect(url)

    login(request, user)

    if request.POST.get("remember_me"):
        request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
    else:
        request.session.set_expiry(0)  # browser session

    return redirect(next_url if next_url else "/")


@require_POST
def register_view(request):
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    password_confirm = request.POST.get("password_confirm", "")
    next_url = request.POST.get("next", "").strip()

    errors = {}
    if not first_name:
        errors["first_name"] = "First name is required."
    if not email:
        errors["email"] = "Email is required."
    if User.objects.filter(email=email).exists():
        errors["email"] = "An account with this email already exists."
    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    if password != password_confirm:
        errors["password_confirm"] = "Passwords do not match."

    if errors:
        for msg in errors.values():
            messages.error(request, msg)
        url = "/auth/?tab=register"
        if next_url:
            url += f"&next={next_url}"
        return redirect(url)

    old_session_key = request.session.session_key

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    login(request, user)

    if old_session_key:
        merge_carts(old_session_key, user)
    messages.success(request, f"Welcome, {user.first_name}! Your account is ready.")
    return redirect(next_url if next_url else "/")


def logout_view(request):
    logout(request)
    messages.success(request, "You've been signed out.")
    return redirect("/")


def _next_or_home(request):
    return request.GET.get("next") or "/"
