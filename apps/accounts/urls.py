from django.urls import path
from apps.accounts.views.register import RegisterView
from apps.accounts.views.login import LoginView
from apps.accounts.views.verify_emails import VerifyEmailView

urlpatterns = [
    path("register/", RegisterView.as_view(),name="register"),
    path("login/", LoginView.as_view(),name='login'),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
]
