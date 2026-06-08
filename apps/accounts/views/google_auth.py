from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.accounts.services.auth import AuthService
from apps.common.utils import Utils


class GoogleAuthView(APIView):
    """
    POST { "credential": "<Google ID token JWT from GIS>", "age": 18 }
    Same response shape as email/password login (success, data.token, ...).
    Age is required only when the Google credential creates a new account.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        credential = request.data.get("credential")
        if not credential or not isinstance(credential, str):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=Utils.error_response_data(
                    message="Missing credential",
                    error=["Request body must include a non-empty 'credential' string (Google ID token)."],
                ),
            )

        result = AuthService.google_auth(credential.strip(), age=request.data.get("age"))
        return Response(status=status.HTTP_200_OK, data=result.to_dict())
