from django.urls import path
from apps.admin_panel import views

urlpatterns = [
    # Auth
    path("admin-panel/login/", views.admin_login, name="ap_login"),
    path("admin-panel/logout/", views.admin_logout, name="ap_logout"),
    # Dashboard
    path("admin-panel/", views.dashboard, name="ap_dashboard"),
    # Products
    path("admin-panel/products/", views.product_list, name="ap_product_list"),
    path("admin-panel/products/add/", views.product_add, name="ap_product_add"),
    path(
        "admin-panel/products/<str:pk>/edit/",
        views.product_edit,
        name="ap_product_edit",
    ),
    path(
        "admin-panel/products/<str:pk>/delete/",
        views.product_delete,
        name="ap_product_delete",
    ),
    path(
        "admin-panel/products/variation/<str:pk>/delete/",
        views.variation_delete,
        name="ap_variation_delete",
    ),
    path(
        "admin-panel/products/gallery/<str:pk>/delete/",
        views.image_delete,
        name="ap_image_delete",
    ),
    path(
        "admin-panel/products/<str:pk>/primary-image/delete/",
        views.primary_image_delete,
        name="ap_primary_image_delete",
    ),
    # Orders
    path("admin-panel/orders/", views.order_list, name="ap_order_list"),
    path(
        "admin-panel/orders/<str:order_number>/",
        views.order_detail,
        name="ap_order_detail",
    ),
    path(
        "admin-panel/orders/<str:order_number>/status/",
        views.order_update_status,
        name="ap_order_status",
    ),
    # Quotes
    path("admin-panel/quotes/", views.quote_list, name="ap_quote_list"),
    path("admin-panel/quotes/<str:pk>/", views.quote_detail, name="ap_quote_detail"),
    path(
        "admin-panel/quotes/<str:pk>/status/",
        views.quote_update_status,
        name="ap_quote_status",
    ),
    # Admin users (superadmin only)
    path("admin-panel/admins/", views.admin_list, name="ap_admin_list"),
    path("admin-panel/admins/add/", views.admin_add, name="ap_admin_add"),
    path("admin-panel/admins/<str:pk>/edit/", views.admin_edit, name="ap_admin_edit"),
    path(
        "admin-panel/admins/<str:pk>/remove/",
        views.admin_remove,
        name="ap_admin_remove",
    ),
    path("admin-panel/categories/", views.category_list, name="ap_category_list"),
    path("admin-panel/categories/add/", views.category_add, name="ap_category_add"),
    path(
        "admin-panel/categories/<str:pk>/edit/",
        views.category_edit,
        name="ap_category_edit",
    ),
    path(
        "admin-panel/categories/<str:pk>/delete/",
        views.category_delete,
        name="ap_category_delete",
    ),
]
