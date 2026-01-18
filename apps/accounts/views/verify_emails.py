from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from apps.common.constants import Constants
from apps.common.utils import Utils

User = get_user_model()

class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get("token")

        try:
            payload = AccessToken(token)
            user = User.objects.get(id=payload["user_id"])

            user.is_verified = True
            user.save(update_fields=["is_verified"])

            return Utils.success_response_data(
                message=Constants.email_verification_success
            )
        
        except Exception:
            return Utils.error_response_data(
                message=Constants.email_verification_failed
            )
