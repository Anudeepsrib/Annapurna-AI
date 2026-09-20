from typing import Any

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings

logger = structlog.get_logger()


class AppError(Exception):
    """Base class for application exceptions."""

    code = "INTERNAL_ERROR"

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details


class PlanGenerationError(AppError):
    code = "PLAN_VALIDATION_FAILED"

    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, details=details)


class LLMUnavailableError(AppError):
    code = "LLM_UNAVAILABLE"

    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE, details=details)


class LLMTimeoutError(LLMUnavailableError):
    code = "LLM_TIMEOUT"


class LLMInvalidResponseError(AppError):
    code = "LLM_INVALID_RESPONSE"

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_502_BAD_GATEWAY)


class ExternalAPIError(AppError):
    code = "EXTERNAL_API_ERROR"

    def __init__(self, service: str, message: str):
        super().__init__(f"{service} Error: {message}", status_code=status.HTTP_502_BAD_GATEWAY)


class NotFoundError(AppError):
    code = "NOT_FOUND"

    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", status_code=status.HTTP_404_NOT_FOUND)


class PantryConflictError(AppError):
    code = "PANTRY_CONFLICT"

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class PantryItemUnresolvedError(AppError):
    code = "PANTRY_ITEM_UNRESOLVED"

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


class PlanConflictError(AppError):
    code = "CONSTRAINT_CONFLICT"

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class IdempotencyConflictError(AppError):
    code = "IDEMPOTENCY_CONFLICT"

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class GroceryCompilationError(AppError):
    code = "GROCERY_COMPILATION_FAILED"

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommandValidationError(AppError):
    code = "COMMAND_UNSUPPORTED"

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


async def app_exception_handler(request: Request, exc: AppError):
    """
    Global handler for AppError and its subclasses.
    Returns a consistent JSON structure.
    """
    content: dict[str, Any] = {
        "error": {
            "message": exc.message,
            "code": exc.code,
            "request_id": getattr(request.state, "request_id", "unknown"),
        }
    }
    if exc.details is not None and settings.DEBUG:
        content["error"]["details"] = exc.details

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unhandled exceptions.
    Prevents 500 Internals from leaking stack traces to the client in production.
    """
    logger.exception("Unhandled exception", path=request.url.path)

    error: dict[str, str] = {
        "message": "Internal Server Error",
        "code": "INTERNAL_ERROR",
        "request_id": getattr(request.state, "request_id", "unknown"),
    }
    if settings.DEBUG:
        error["details"] = str(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": error},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error: dict[str, Any] = {
        "message": "Request validation failed",
        "code": "VALIDATION_ERROR",
        "request_id": getattr(request.state, "request_id", "unknown"),
    }
    if settings.DEBUG:
        error["details"] = exc.errors()
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"error": error},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = "NOT_FOUND" if exc.status_code == status.HTTP_404_NOT_FOUND else "HTTP_ERROR"
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": message,
                "code": code,
                "request_id": getattr(request.state, "request_id", "unknown"),
            }
        },
    )
