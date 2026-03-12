from __future__ import annotations

import functools
import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django_ratelimit.core import is_ratelimited

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────

RATE_LIMITS = {
    # Auth
    "login": ("10/h", "ip"),
    "register": ("5/h", "ip"),
    "forgot_password": ("5/h", "ip"),
    "reset_password": ("10/h", "ip"),
    "resend_verification": ("3/h", "user"),
    "password_change": ("10/h", "user"),
    # Checkout
    "initialize_payment": ("10/h", "user"),
    "verify_payment": ("20/h", "ip"),
    "paystack_webhook": ("100/m", "ip"),
    # Cart
    "add_to_cart": ("60/m", "ip"),
    "cart_count": ("60/m", "ip"),
    "cart_drawer": ("60/m", "ip"),
    # Quotes
    "submit_quote": ("5/h", "ip"),
    "submit_general_quote": ("5/h", "ip"),
    # Admin
    "admin_login": ("5/h", "ip"),
}

BLOCK_MESSAGE = "Too many attempts. Please try again later."


def _key_ip(group, request):
    """Rate limit key: client IP address."""
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _key_user(group, request):
    """Rate limit key: authenticated user ID."""
    if request.user.is_authenticated:
        return str(request.user.pk)
    return _key_ip(group, request)


def _get_key_fn(key_type: str):
    return _key_user if key_type == "user" else _key_ip


def _redirect_response(request, redirect_to: str | None):
    """HTML view blocked — redirect back with error message."""
    messages.error(request, BLOCK_MESSAGE)
    target = redirect_to or request.META.get("HTTP_REFERER") or "/"
    return redirect(target)


def _json_response():
    """AJAX/JSON view blocked — return 429."""
    return JsonResponse(
        {"ok": False, "error": BLOCK_MESSAGE},
        status=429,
    )


def ratelimit(
    name: str,
    redirect_to: str | None = None,
    is_json: bool = False,
    method: str | list = "POST",
):
    """
    Decorator that rate limits a view by name.

    Looks up rate and key strategy from RATE_LIMITS.
    - HTML views (is_json=False): redirects with error message on block.
    - JSON/AJAX views (is_json=True): returns 429 JSON on block.

    Usage:
        @ratelimit("login", redirect_to="login")
        def login_view(request): ...

        @ratelimit("add_to_cart", is_json=True)
        def add_to_cart(request): ...
    """
    if name not in RATE_LIMITS:
        raise ValueError(f"Unknown rate limit name: '{name}'. Add it to RATE_LIMITS.")

    rate, key_type = RATE_LIMITS[name]
    key_fn = _get_key_fn(key_type)
    methods = [method] if isinstance(method, str) else method

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.method in methods:
                blocked = is_ratelimited(
                    request,
                    group=f"dm_{name}",
                    key=key_fn,
                    rate=rate,
                    increment=True,
                )
                if blocked:
                    logger.warning(
                        "Rate limit hit: view=%s key_type=%s ip=%s user=%s",
                        name,
                        key_type,
                        _key_ip(f"dm_{name}", request),
                        request.user.pk if request.user.is_authenticated else "anon",
                    )
                    if is_json:
                        return _json_response()
                    return _redirect_response(request, redirect_to)

            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


# Auth
limit_login = ratelimit("login", redirect_to="login", is_json=False)
limit_register = ratelimit("register", redirect_to="register", is_json=False)
limit_forgot_password = ratelimit("forgot_password", redirect_to="forgot_password", is_json=False)
limit_reset_password = ratelimit("reset_password", is_json=False)
limit_resend_verification = ratelimit("resend_verification", is_json=False)
limit_password_change = ratelimit("password_change", is_json=False)

# Checkout
limit_initialize_payment = ratelimit("initialize_payment", is_json=True)
limit_verify_payment = ratelimit("verify_payment", is_json=True)
limit_paystack_webhook = ratelimit("paystack_webhook", is_json=True, method="POST")

# Cart
limit_add_to_cart = ratelimit("add_to_cart", is_json=True)
limit_cart_count = ratelimit("cart_count", is_json=True, method=["GET", "POST"])
limit_cart_drawer = ratelimit("cart_drawer", is_json=True, method=["GET", "POST"])

# Quotes
limit_submit_quote = ratelimit("submit_quote", is_json=True)
limit_submit_general_quote = ratelimit("submit_general_quote", is_json=True)

# Admin
limit_admin_login = ratelimit("admin_login", redirect_to="admin_login", is_json=False)
