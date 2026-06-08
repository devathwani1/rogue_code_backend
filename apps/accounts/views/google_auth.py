from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny

from apps.accounts.services.auth import AuthService


class GoogleAuthSerializer(serializers.Serializer):
    credential = serializers.CharField()
    temporary_login = serializers.BooleanField(required=False, default=False)


class GoogleAuthView(APIView):
    """
    POST { "credential": "<Google ID token JWT from GIS>" }
    Same response shape as email/password login (success, data.token, ...).
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = AuthService.google_auth(
            serializer.validated_data["credential"].strip(),
            temporary_login=serializer.validated_data["temporary_login"],
        )
        return Response(status=status.HTTP_200_OK, data=result.to_dict())
