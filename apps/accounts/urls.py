from django.urls import path
from apps.accounts.views.register import RegisterView
from apps.accounts.views.login import LoginView
from apps.accounts.views.verify_emails import VerifyEmailView
from apps.accounts.views.admin_users import AdminUserListView
from apps.accounts.views.password_reset import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
)
from apps.accounts.views.google_auth import GoogleAuthView

urlpatterns = [
    path("register/", RegisterView.as_view(),name="register"),
    path("login/", LoginView.as_view(),name='login'),
    path("google/", GoogleAuthView.as_view(), name="google-auth"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("admin/users/", AdminUserListView.as_view(), name="admin-users-list"),
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
