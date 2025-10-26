class ServiceError(Exception):
    """Base class for all service-level exceptions"""
    status_code: int = 500
    detail: str = "An internal error occured."

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail) # super() refers to `Exception` 

class AuthError(ServiceError):
    """Base for authentication/authorization errors."""
    status_code = 401
    detail = "Authentication error."

class UsernameTakenError(AuthError):
    status_code = 400
    detail = "Username already taken"

class InvalidCredentialsError(AuthError):
    status_code = 401
    detail = "Invalid username or password"
