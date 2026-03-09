from .admins import admin_add, admin_edit, admin_list, admin_remove
from .auth import admin_login, admin_logout
from .categories import (
    category_add,
    category_delete,
    category_edit,
    category_list,
)
from .dashboard import dashboard
from .orders import order_detail, order_list, order_update_status
from .products import (
    product_list,
    product_add,
    product_edit,
    product_delete,
    variation_delete,
    image_delete,
    primary_image_delete,
)
from .quotes import quote_detail, quote_list, quote_update_status

__all__ = [
    "dashboard",
    "admin_login",
    "admin_logout",
    "product_list",
    "product_add",
    "product_edit",
    "product_delete",
    "variation_delete",
    "image_delete",
    "primary_image_delete",
    "order_list",
    "order_detail",
    "order_update_status",
    "quote_list",
    "quote_detail",
    "quote_update_status",
    "admin_list",
    "admin_add",
    "admin_edit",
    "admin_remove",
    "category_list",
    "category_add",
    "category_edit",
    "category_delete",
]
