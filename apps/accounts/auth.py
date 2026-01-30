from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from apps.accounts.services.auth_result import AuthState, ActionRequired

class CustomJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)

        if user_auth_tuple is None:
            return None

        user, token = user_auth_tuple

        if not getattr(user, "is_verified", False):
            raise exceptions.PermissionDenied(detail={
                "auth_state": AuthState.NOT_VERIFIED,
                "action_required": ActionRequired.VERIFY_EMAIL,
                "message": "Email not verified"
            })

        return (user, token)
