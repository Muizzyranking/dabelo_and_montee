from functools import wraps

from django.http import Http404
from django.shortcuts import redirect


def get_admin_profile(user):
    """Returns AdminProfile or None."""
    if not user.is_authenticated or not user.is_staff:
        return None
    try:
        return user.admin_profile
    except Exception:
        return None


def is_superadmin(user):
    profile = get_admin_profile(user)
    return profile and profile.is_superadmin


def admin_required(perm=None):
    """
    Decorator that gates views by admin permission.
    perm = None means just needs to be any admin.
    perm = "can_view_orders" etc checks specific permission.
    Superadmin always passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            profile = get_admin_profile(request.user)
            if not profile:
                return redirect("/admin-panel/login/")

            if profile.is_superadmin:
                return view_func(request, *args, **kwargs)

            if perm and not getattr(profile, perm, False):
                raise Http404

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def superadmin_required(view_func):
    """Only superadmins."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = get_admin_profile(request.user)
        if not profile or not profile.is_superadmin:
            if not profile:
                return redirect("/admin-panel/login/")
            raise Http404
        return view_func(request, *args, **kwargs)

    return _wrapped
