from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.admin_panel.permissions import get_admin_profile
from core.rate_limit import limit_admin_login


@limit_admin_login
def admin_login(request):
    if request.user.is_authenticated:
        profile = get_admin_profile(request.user)
        if profile:
            return redirect("ap_dashboard")

    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)

        if user and get_admin_profile(user):
            login(request, user)
            return redirect("ap_dashboard")
        else:
            error = "Invalid credentials or insufficient permissions."

    return render(request, "admin_panel/login.html", {"error": error})


@require_POST
def admin_logout(request):
    logout(request)
    return redirect("ap_login")
