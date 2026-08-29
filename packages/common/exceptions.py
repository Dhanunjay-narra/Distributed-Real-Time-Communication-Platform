from typing import Any, Dict, Optional

class ChatbotException(Exception):
    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL_SERVER_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message, self.status_code, self.error_code, self.details = message, status_code, error_code, details or {}
    def to_dict(self) -> Dict[str, Any]:
        return {"success": False, "error": {"code": self.error_code, "message": self.message, "details": self.details}}

class NotFoundException(ChatbotException):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 404, "NOT_FOUND", details)

class UnauthorizedException(ChatbotException):
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, "UNAUTHORIZED", details)

class ForbiddenException(ChatbotException):
    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, "FORBIDDEN", details)

class ConflictException(ChatbotException):
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 409, "CONFLICT", details)

class ValidationException(ChatbotException):
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 422, "VALIDATION_ERROR", details)

class RateLimitException(ChatbotException):
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(message, 429, "RATE_LIMIT_EXCEEDED", {"retry_after": retry_after})

class ServiceUnavailableException(ChatbotException):
    def __init__(self, message: str = "Service temporarily unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 503, "SERVICE_UNAVAILABLE", details)
