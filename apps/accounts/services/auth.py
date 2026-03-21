import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from apps.accounts.services.auth_result import AuthResult, AuthState, ActionRequired
from django.contrib.auth.hashers import check_password
from apps.profiles.models.profile import Profile

User = get_user_model()

logger = logging.getLogger(__name__)


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

    @staticmethod
    def google_auth(credential: str) -> AuthResult:
        """
        Verify Google ID token (JWT) from GIS, then sign up or sign in by email.
        """
        client_ids = (
            getattr(settings, "GOOGLE_OAUTH_CLIENT_IDS", None)
            or getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")
            or ""
        )
        if isinstance(client_ids, str):
            client_ids = [client_ids.strip()] if client_ids.strip() else []
        if not client_ids:
            return AuthResult(
                success=False,
                auth_state=AuthState.NOT_AUTHENTICATED,
                message="Google sign-in is not configured on the server (missing GOOGLE_OAUTH_CLIENT_ID).",
            )

        try:
            import jwt as pyjwt
            import requests
            from google.oauth2 import id_token
            from google.auth.transport import requests as google_requests
            from google.auth.exceptions import GoogleAuthError, TransportError
        except ImportError as exc:
            # Usually: venv not activated, or `pip install -r requirements.txt` not run in that env.
            # On Debian/Ubuntu, system Python cannot use pip without a venv (PEP 668).
            hint = (
                "Create a virtual environment in rogue_code_backend, activate it, then run: "
                "python -m pip install -r requirements.txt — use the same Python you use for "
                "manage.py runserver. If you use a different machine, run `pip install google-auth PyJWT requests` there."
            )
            if getattr(settings, "DEBUG", False):
                hint += f" ImportError: {exc!r}"
            return AuthResult(
                success=False,
                auth_state=AuthState.NOT_AUTHENTICATED,
                message="Google sign-in is not available: " + hint,
            )
        idinfo = None
        last_exc: Exception | None = None
        request = google_requests.Request()
        for client_id in client_ids:
            try:
                idinfo = id_token.verify_oauth2_token(
                    credential,
                    request,
                    client_id,
                )
                break
            except (TransportError, requests.exceptions.RequestException) as exc:
                # Certificate / JWKS fetch from Google failed (network, SSL, proxy, firewall).
                logger.warning("Google OAuth transport error while verifying token: %s", exc)
                return AuthResult(
                    success=False,
                    auth_state=AuthState.NOT_AUTHENTICATED,
                    message=(
                        "Cannot reach Google to verify sign-in. Check this server's internet access, "
                        "firewall, proxy, and SSL certificates."
                    ),
                )
            except (ValueError, GoogleAuthError, pyjwt.exceptions.PyJWTError) as exc:
                # Wrong audience / bad or expired token — try next configured Web Client ID.
                last_exc = exc
                continue

        if idinfo is None:
            if getattr(settings, "DEBUG", False) and last_exc is not None:
                logger.warning(
                    "Google ID token verification failed for all client IDs: %s",
                    last_exc,
                )
            return AuthResult(
                success=False,
                auth_state=AuthState.NOT_AUTHENTICATED,
                message="Invalid or expired Google sign-in. Please try again.",
            )

        iss = idinfo.get("iss")
        if iss not in ("accounts.google.com", "https://accounts.google.com"):
            return AuthResult(
                success=False,
                auth_state=AuthState.NOT_AUTHENTICATED,
                message="Invalid Google token issuer.",
            )

        email = (idinfo.get("email") or "").strip().lower()
        if not email:
            return AuthResult(
                success=False,
                auth_state=AuthState.NOT_AUTHENTICATED,
                message="Google did not provide an email address.",
            )
        def _claim_truthy(value) -> bool:
            if value is True:
                return True
            if isinstance(value, str) and value.lower() in ("true", "1", "yes"):
                return True
            return False

        if not _claim_truthy(idinfo.get("email_verified")):
            return AuthResult(
                success=False,
                auth_state=AuthState.NOT_AUTHENTICATED,
                message="Your Google email must be verified to continue.",
            )

        user = User.get_user_by_email(email)

        if user:
            if not user.is_verified:
                user.is_verified = True
                user.save(update_fields=["is_verified"])
            token = AuthService.generate_tokens(user)
            return AuthResult(
                success=True,
                auth_state=AuthState.SUCCESS,
                message="Signed in with Google.",
                data={"token": token},
            )

        with transaction.atomic():
            user = User(
                username=email,
                email=email,
                is_active=True,
                is_verified=True,
            )
            user.set_unusable_password()
            user.save()
            Profile.objects.create(user=user)

        token = AuthService.generate_tokens(user)
        return AuthResult(
            success=True,
            auth_state=AuthState.SUCCESS,
            message="Welcome! Your account was created with Google.",
            data={"token": token},
        )