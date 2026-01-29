from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.serializers.login import LoginSerializer
from apps.accounts.services.auth import AuthService


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = AuthService.login(serializer.validated_data)
        return Response(status=status.HTTP_200_OK, data=response.to_dict())
