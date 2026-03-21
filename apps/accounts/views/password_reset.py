from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.serializers.password_reset import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
)
from apps.common.utils import Utils

logger = logging.getLogger(__name__)
token_generator = PasswordResetTokenGenerator()


def _uid_encode(user: User) -> str:
    return urlsafe_base64_encode(force_bytes(str(user.pk)))


def _uid_decode(uidb64: str) -> str | None:
    try:
        return force_str(urlsafe_base64_decode(uidb64))
    except (TypeError, ValueError, OverflowError):
        return None


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PasswordResetRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].strip().lower()

        user = User.objects.filter(email__iexact=email).first()
        if user and user.is_active:
            uid = _uid_encode(user)
            token = token_generator.make_token(user)
            reset_url = f"{settings.FRONTEND_URL.rstrip('/')}/new_pass?uid={uid}&token={token}"

            subject = "Reset your Rogue Code password"
            body = (
                "You requested a password reset for your Rogue Code account.\n\n"
                f"Open this link to choose a new password (valid for a limited time):\n{reset_url}\n\n"
                "If you did not request this, you can ignore this email."
            )
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(
                settings, "EMAIL_HOST_USER", None
            )
            try:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=from_email,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception:
                logger.exception("password_reset: failed to send email to %s", user.email)
                if settings.DEBUG:
                    logger.info("password_reset: dev fallback link %s", reset_url)

        # Same response whether or not the user exists (avoid email enumeration)
        return Response(
            Utils.success_response_data(
                message="If an account exists for that email, you will receive password reset instructions shortly.",
                data=None,
            ),
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PasswordResetConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        uidb64 = ser.validated_data["uid"]
        token = ser.validated_data["token"]
        new_password = ser.validated_data["new_password"]

        pk_str = _uid_decode(uidb64)
        if not pk_str:
            return Response(
                data=Utils.error_response_data(
                    message="Invalid reset link",
                    error=["The password reset link is invalid."],
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=pk_str)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                data=Utils.error_response_data(
                    message="Invalid reset link",
                    error=["The password reset link is invalid or has expired."],
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not token_generator.check_token(user, token):
            return Response(
                data=Utils.error_response_data(
                    message="Invalid or expired token",
                    error=[
                        "This reset link is invalid or has expired. Please request a new one."
                    ],
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user)
        except DjangoValidationError as e:
            return Response(
                data=Utils.error_response_data(
                    message="Password does not meet requirements",
                    error=list(e.messages),
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response(
            Utils.success_response_data(
                message="Your password has been reset. You can sign in with your new password.",
                data=None,
            ),
            status=status.HTTP_200_OK,
        )
