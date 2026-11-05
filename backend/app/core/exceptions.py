"""Custom exceptions"""


class AppException(Exception):
    """Base exception for application errors"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UnauthorizedException(AppException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    """Raised when user lacks required permissions"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class NotFoundException(AppException):
    """Raised when a resource is not found"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class BadRequestException(AppException):
    """Raised when request is invalid"""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=400)


class ConflictException(AppException):
    """Raised when there's a conflict (e.g., duplicate resource)"""

    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status_code=409)


class ValidationException(AppException):
    """Raised when validation fails"""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)
