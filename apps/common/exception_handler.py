from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.services.auth_result import AuthState

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Check if the exception detail has our custom fields
        if isinstance(response.data, dict):
            auth_state = response.data.get("auth_state")
            action_required = response.data.get("action_required")
            message = response.data.get("message") or response.data.get("detail")

            # Handle NotAuthenticated specifically if not already set
            if response.status_code == status.HTTP_401_UNAUTHORIZED and not auth_state:
                auth_state = AuthState.NOT_AUTHENTICATED
                message = "Authentication credentials were not provided."

            if auth_state:
                response.data = {
                    "success": False,
                    "auth_state": auth_state,
                    "action_required": action_required,
                    "message": message,
                    "data": {}
                }

    return response
