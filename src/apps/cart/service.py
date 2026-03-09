from django.contrib.auth import get_user_model

from .models import Cart, CartItem

User = get_user_model()


def get_or_create_cart(request):
    """Get or create the cart for the current request."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart


def add_item(request, product, variation=None, quantity=1):
    """Add item to cart or increment quantity if already exists."""
    cart = get_or_create_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, variation=variation, defaults={"quantity": quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    return cart, item, created


def update_quantity(request, item_id, quantity):
    """Update item quantity. Removes item if quantity <= 0."""
    cart = get_or_create_cart(request)
    try:
        item = cart.items.get(pk=item_id)
        if quantity <= 0:
            item.delete()
            return cart, None
        item.quantity = quantity
        item.save()
        return cart, item
    except CartItem.DoesNotExist:
        return cart, None


def remove_item(request, item_id):
    """Remove a single item from cart."""
    cart = get_or_create_cart(request)
    cart.items.filter(pk=item_id).delete()
    return cart


def clear_cart(request):
    """Remove all items from cart."""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    return cart


def merge_carts(session_key, user):
    if not session_key:
        return

    if not isinstance(user, User):
        return

    session_cart = Cart.objects.filter(session_key=session_key).first()

    if not session_cart:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    if session_cart.pk != user_cart.pk:
        user_cart.merge_with(session_cart)


def merge_carts_on_login(request, user):
    """
    Merge session cart into user cart after login.
    Called from the login signal.
    """
    if not request.session.session_key:
        return

    merge_carts(request.session.session_key, user)
