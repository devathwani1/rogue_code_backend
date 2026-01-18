from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

User = get_user_model()

class AuthService:

    @staticmethod
    def generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token),
        

    @staticmethod
    def send_verification_email(user, request):
        token = RefreshToken.for_user(user).access_token
        verify_url = request.build_absolute_uri(
            reverse("verify-email") + f"?token={token}"
        )

        send_mail(
            subject="Verify your email",
            message=f"Click to verify: {verify_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
