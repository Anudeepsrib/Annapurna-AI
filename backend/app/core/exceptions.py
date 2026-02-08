from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict

class AppError(Exception):
    """Base class for application exceptions."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details

class PlanGenerationError(AppError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)

class ExternalAPIError(AppError):
    def __init__(self, service: str, message: str):
        super().__init__(f"{service} Error: {message}", status_code=status.HTTP_502_BAD_GATEWAY)

class NotFoundError(AppError):
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", status_code=status.HTTP_404_NOT_FOUND)

async def app_exception_handler(request: Request, exc: AppError):
    """
    Global handler for AppError and its subclasses.
    Returns a consistent JSON structure.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details,
                "code": exc.__class__.__name__
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unhandled exceptions.
    Prevents 500 Internals from leaking stack traces to the client in production.
    """
    # In a real app, you would log the full stack trace here via structlog/sentry
    print(f"Unhandled Exception: {exc}") 
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal Server Error",
                "code": "InternalServerError"
            }
        }
    )
