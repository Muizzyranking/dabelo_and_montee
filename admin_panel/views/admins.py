from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from admin_panel.permissions import superadmin_required
from admin_panel.models import AdminProfile

User = get_user_model()

PERMISSION_FIELDS = [
    ("can_view_dabelo_products", "View Dabelo Products"),
    ("can_edit_dabelo_products", "Edit Dabelo Products"),
    ("can_view_montee_products", "View Motee Products"),
    ("can_edit_montee_products", "Edit Motee Products"),
    ("can_view_orders", "View Orders"),
    ("can_edit_orders", "Edit Orders"),
    ("can_view_quotes", "View Quote Requests"),
    ("can_edit_quotes", "Edit Quote Requests"),
    ("can_manage_images", "Manage Product Images"),
]


@superadmin_required
def admin_list(request):
    profiles = AdminProfile.objects.select_related("user").order_by(
        "-is_superadmin", "user__email"
    )
    return render(
        request,
        "admin_panel/admins/list.html",
        {
            "profiles": profiles,
        },
    )


@superadmin_required
def admin_add(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()
        fname = request.POST.get("first_name", "").strip()
        lname = request.POST.get("last_name", "").strip()

        errors = {}
        if not email:
            errors["email"] = "Email is required."
        if not password:
            errors["password"] = "Password is required."
        if User.objects.filter(email=email).exists():
            errors["email"] = "A user with this email already exists."

        if errors:
            for msg in errors.values():
                messages.error(request, msg)
            return redirect("ap_admin_add")

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=fname,
            last_name=lname,
            is_staff=True,
        )

        profile = AdminProfile.objects.create(
            user=user,
            is_superadmin=request.POST.get("is_superadmin") == "on",
        )

        # Set permissions
        for field, _ in PERMISSION_FIELDS:
            setattr(profile, field, request.POST.get(field) == "on")
        profile.save()

        messages.success(request, f"Admin account created for {email}.")
        return redirect("ap_admin_list")

    return render(
        request,
        "admin_panel/admins/form.html",
        {
            "mode": "add",
            "fields": PERMISSION_FIELDS,
        },
    )


@superadmin_required
def admin_edit(request, pk):
    profile = get_object_or_404(AdminProfile, pk=pk)

    if request.method == "POST":
        profile.user.first_name = request.POST.get("first_name", "").strip()
        profile.user.last_name = request.POST.get("last_name", "").strip()
        profile.user.save()

        profile.is_superadmin = request.POST.get("is_superadmin") == "on"
        for field, _ in PERMISSION_FIELDS:
            setattr(profile, field, request.POST.get(field) == "on")
        profile.save()

        # Optionally update password
        new_pw = request.POST.get("new_password", "").strip()
        if new_pw:
            profile.user.set_password(new_pw)
            profile.user.save()

        messages.success(request, "Admin updated.")
        return redirect("ap_admin_list")

    return render(
        request,
        "admin_panel/admins/form.html",
        {
            "mode": "edit",
            "profile": profile,
            "fields": PERMISSION_FIELDS,
        },
    )


@require_POST
@superadmin_required
def admin_remove(request, pk):
    profile = get_object_or_404(AdminProfile, pk=pk)

    if profile.user == request.user:
        messages.error(request, "You cannot remove your own admin account.")
        return redirect("ap_admin_list")

    profile.user.is_staff = False
    profile.user.save()
    profile.delete()
    messages.success(request, "Admin removed.")
    return redirect("ap_admin_list")
