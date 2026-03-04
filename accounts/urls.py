from django.urls import path
from accounts.views import account_views, auth

urlpatterns = [
    # Auth
    path("auth/", auth.auth_page, name="auth"),
    path("auth/login/", auth.login_view, name="login"),
    path("auth/register/", auth.register_view, name="register"),
    path("auth/logout/", auth.logout_view, name="logout"),
    # Account
    path("account/", account_views.dashboard, name="account_dashboard"),
    path("account/orders/", account_views.order_list, name="account_orders"),
    path(
        "account/orders/<str:order_number>/",
        account_views.order_detail,
        name="account_order_detail",
    ),
    path("account/quotes/", account_views.quote_list, name="account_quotes"),
    path("account/profile/", account_views.profile, name="account_profile"),
    path("account/address/", account_views.address, name="account_address"),
    path("account/password/", account_views.change_password, name="account_password"),
]
