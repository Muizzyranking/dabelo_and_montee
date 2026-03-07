from __future__ import annotations

import json
import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cart.service import clear_cart
from products.models import Order

from .services import (
    PAYSTACK_PUBLIC,
    CheckoutService,
    CheckoutSessionService,
    OrderService,
    PaystackService,
)

logger = logging.getLogger(__name__)


@login_required(login_url="/auth/")
def checkout(request):
    cart, err = CheckoutService.get_valid_cart(request)
    if err:
        return redirect("cart")

    items = cart.items.select_related("product", "variation").prefetch_related(
        "product__images"
    )
    user = request.user

    context = {
        "cart": cart,
        "items": items,
        "subtotal": cart.subtotal,
        "total": cart.subtotal,
        "user": user,
        "paystack_public": PAYSTACK_PUBLIC,
        "address": {
            "name": user.full_name,
            "phone": user.phone,
            "line1": user.address_line_1,
            "line2": user.address_line_2,
            "city": user.city,
            "state": user.state,
        },
    }
    return render(request, "checkout/checkout.html", context)


@login_required(login_url="/auth/")
@require_POST
def initialize_payment(request):
    cart, err = CheckoutService.get_valid_cart(request)
    if err:
        return JsonResponse({"ok": False, "message": err}, status=400)

    address, errors = CheckoutService.validate_address(request.POST)
    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    subtotal = cart.subtotal
    total = subtotal  # delivery free for now

    if total <= 0:
        return JsonResponse(
            {"ok": False, "message": "Cart total is invalid."}, status=400
        )

    reference = PaystackService.generate_reference()

    OrderService.create_pending_order(
        user=request.user,
        cart=cart,
        address=address,
        reference=reference,
        total=total,
        subtotal=subtotal,
    )

    CheckoutSessionService.set_reference(request.session, reference)

    return JsonResponse(
        {
            "ok": True,
            "reference": reference,
            "amount": int(total * 100),
            "email": request.user.email,
            "key": PAYSTACK_PUBLIC,
        }
    )


@login_required(login_url="/auth/")
def verify_payment(request):
    session_reference = CheckoutSessionService.get_reference(request.session)
    url_reference = request.GET.get("reference")

    if not session_reference:
        messages.error(request, "Checkout session not found. Please try again.")
        return redirect("cart")

    # Consistency check — if Paystack sends a ref in the URL it must match
    if url_reference and url_reference != session_reference:
        logger.warning(
            "verify_payment: reference mismatch session=%s url=%s user=%s",
            session_reference,
            url_reference,
            request.user.id,
        )
        messages.error(request, "Payment reference mismatch. Please contact us.")
        return redirect("cart")

    reference = session_reference

    try:
        ps_data = PaystackService.verify_transaction(reference)
    except ValueError:
        messages.error(
            request,
            "Payment verification failed. If you were charged, please contact us.",
        )
        return redirect("checkout")

    if ps_data.get("status") != "success":
        messages.error(request, "Payment was not completed.")
        return redirect("checkout")

    paid_total = Decimal(ps_data.get("amount", 0)) / 100  # kobo → naira

    try:
        order = OrderService.confirm_order(
            user=request.user,
            reference=reference,
            paid_amount=paid_total,
            gateway_response=json.dumps(ps_data),
        )
    except ValueError as exc:
        error = str(exc)
        if error == "amount_mismatch":
            messages.error(request, "Payment amount mismatch. Please contact us.")
        elif error == "not_found":
            messages.error(request, "Order not found. Please contact us.")
        else:
            messages.error(request, "Something went wrong. Please contact us.")
        return redirect("cart")

    clear_cart(request)
    CheckoutSessionService.set_confirmed_order(request.session, order.order_number)
    CheckoutSessionService.clear(request.session)

    return redirect("order_confirmation", order_number=order.order_number)


@csrf_exempt
@require_POST
def paystack_webhook(request):
    signature = request.headers.get("X-Paystack-Signature", "")

    if not PaystackService.verify_webhook_signature(request.body, signature):
        logger.warning("Paystack webhook received with invalid signature")
        return HttpResponse(status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    if payload.get("event") == "charge.success":
        data = payload.get("data", {})
        reference = data.get("reference")
        if reference:
            OrderService.confirm_order_from_webhook(
                reference=reference,
                gateway_response=json.dumps(data),
            )

    return HttpResponse(status=200)


@login_required(login_url="/auth/")
def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    items = order.items.select_related("product")
    return render(
        request,
        "checkout/confirmation.html",
        {"order": order, "items": items},
    )
