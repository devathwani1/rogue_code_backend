from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status
from apps.common.utils import Utils
from apps.common.constants import Constants
from apps.accounts.services.auth_result import AuthResult, AuthState, ActionRequired
from django.contrib.auth.hashers import check_password
User = get_user_model()

class AuthService:

    @staticmethod
    def generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
        

    @staticmethod
    def send_verification_email(user, request):
        token = AuthService.generate_tokens(user)
        verify_url = f"{settings.FRONTEND_URL}/verifyEmail?token={token}"

        send_mail(
            subject="Verify your email",
            message=f"Click to verify: {verify_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    @staticmethod
    def login(validated_data):
        user = User.get_user_by_email(validated_data["email"])
        if not user:
            return AuthResult(
                success=False,
                auth_state=AuthState.USER_NOT_FOUND,
                message="User not found",
            )
        
        if check_password(validated_data["password"], user.password) is False:
            return AuthResult(
                success=False,
                auth_state=AuthState.WRONG_PASSWORD,
                message="Wrong Password",
            )

        if not user.is_verified:
            return AuthResult(
                success=False,
                auth_state=AuthState.EMAIL_NOT_VERIFIED,
                action_required=ActionRequired.VERIFY_EMAIL,
                message="Email not verified",
            )

        tokens = AuthService.generate_tokens(user)
        return AuthResult(
            success=True,
            auth_state=AuthState.SUCCESS,
            message="Login successful",
            data={"token": tokens},
        )