class AuthResult:
    def __init__(
        self,
        success: bool,
        auth_state: str,
        message: str = None,
        action_required: str = None,
        data: dict = None,
    ):
        self.success = success
        self.auth_state = auth_state
        self.message = message
        self.action_required = action_required
        self.data = data or {}

    def to_dict(self):
        return {
            "success": self.success,
            "auth_state": self.auth_state,
            "action_required": self.action_required,
            "message": self.message,
            "data": self.data,
        }

class AuthState:
    USER_NOT_FOUND = "USER_NOT_FOUND"
    WRONG_PASSWORD = "WRONG_PASSWORD"
    EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"
    EMAIL_ALREADY_REGISTERED = "EMAIL_ALREADY_REGISTERED"
    INVALID_AGE = "INVALID_AGE"
    SUCCESS = "SUCCESS"
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    NOT_VERIFIED = "NOT_VERIFIED"

class ActionRequired:
    VERIFY_EMAIL = "VERIFY_EMAIL"
    LOGIN = "LOGIN"
