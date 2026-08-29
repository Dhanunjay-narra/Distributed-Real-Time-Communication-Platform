from typing import Optional, Dict, Any

class DomainException(Exception):
    def __init__(self, message: str, code: str = "DOMAIN_ERROR", status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

class UnauthorizedException(DomainException):
    def __init__(self, message: str = "Authentication required or credentials invalid", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="UNAUTHORIZED", status_code=401, details=details)

class ForbiddenException(DomainException):
    def __init__(self, message: str = "Access to requested resource is forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="FORBIDDEN", status_code=403, details=details)

class NotFoundException(DomainException):
    def __init__(self, message: str = "Requested resource does not exist", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="NOT_FOUND", status_code=404, details=details)

class ConflictException(DomainException):
    def __init__(self, message: str = "Conflict with existing resource state", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONFLICT", status_code=409, details=details)

class ValidationException(DomainException):
    def __init__(self, message: str = "Request payload validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_FAILED", status_code=422, details=details)

class RateLimitExceededException(DomainException):
    def __init__(self, message: str = "Too many requests. Please slow down.", retry_after_seconds: int = 60):
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", status_code=429, details={"retry_after": retry_after_seconds})

class CircuitBreakerOpenException(DomainException):
    def __init__(self, message: str = "Service circuit breaker is open. Request short-circuited."):
        super().__init__(message, code="CIRCUIT_BREAKER_OPEN", status_code=503)

class SagaExecutionException(DomainException):
    def __init__(self, message: str, saga_id: str, failed_step: str):
        super().__init__(message, code="SAGA_FAILED", status_code=500, details={"saga_id": saga_id, "failed_step": failed_step})

class DistributedLockException(DomainException):
    def __init__(self, message: str = "Failed to acquire distributed lock lease"):
        super().__init__(message, code="LOCK_ACQUISITION_FAILED", status_code=503)

ChatbotException = DomainException
RateLimitException = RateLimitExceededException
ServiceUnavailableException = CircuitBreakerOpenException
