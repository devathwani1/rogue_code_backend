from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.serializers.register import RegisterSerializer
from apps.accounts.services.auth import AuthService
from apps.common.utils import Utils
from apps.common.constants import Constants

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        AuthService.send_verification_email(user, request)

        tokens = AuthService.generate_tokens(user)

        return Utils.success_response_data(
            message=Constants.registration_successful,
            data={"tokens": tokens}
        )
