from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.serializers.register import RegisterSerializer
from apps.accounts.services.auth import AuthService
from apps.common.utils import Utils
from apps.common.constants import Constants
from apps.accounts.services.auth_result import AuthResult, AuthState, ActionRequired
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = User.get_user_by_email(email)

        if user:
            if not user.is_verified:
                auth_result = AuthResult(
                    success=False,
                    auth_state=AuthState.EMAIL_NOT_VERIFIED,
                    action_required=ActionRequired.VERIFY_EMAIL,
                    message="Email already registered but not verified."
                )
            else:
                auth_result = AuthResult(
                    success=False,
                    auth_state=AuthState.EMAIL_ALREADY_REGISTERED,
                    action_required=ActionRequired.LOGIN,
                    message="Email already registered. Please login."
                )
            return Response(status=status.HTTP_200_OK, data=auth_result.to_dict())

        serializer = RegisterSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        auth_result = AuthResult(
            success=True,
            auth_state=AuthState.SUCCESS,
            message=Constants.registration_success,
            action_required=ActionRequired.VERIFY_EMAIL
        )
        return Response(status=status.HTTP_201_CREATED, data=auth_result.to_dict())
