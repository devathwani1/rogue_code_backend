from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from apps.common.constants import Constants
from apps.common.utils import Utils
from apps.accounts.services.auth_result import AuthResult, AuthState

User = get_user_model()

class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get("token")

        try:
            payload = AccessToken(token)
            user = User.objects.get(user_id=payload["user_id"])

            user.is_verified = True
            user.save()

            return Response(
                AuthResult(
                    success=True,
                    auth_state=AuthState.SUCCESS,
                    message=Constants.email_verification_success
                ).to_dict()
            )
        
        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=AuthResult(
                    success=False,
                    auth_state=AuthState.USER_NOT_FOUND, # Or a more broad error state
                    message=f"{Constants.email_verification_failed}: {str(e)}"
                ).to_dict()
            )
