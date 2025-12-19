"""Custom exception handling for consistent API responses."""
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """
    Custom exception handler that provides consistent error responses.
    
    Response format:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "details": {} // Optional additional details
        }
    }
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is None:
        return None
    
    # Standardize error response format
    error_response = {
        "error": {
            "code": _get_error_code(response.status_code),
            "message": _get_error_message(response.data),
            "details": response.data if isinstance(response.data, dict) else {"detail": response.data},
        }
    }
    
    response.data = error_response
    return response


def _get_error_code(status_code: int) -> str:
    """Map HTTP status codes to error codes."""
    error_codes = {
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
        status.HTTP_409_CONFLICT: "CONFLICT",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
        status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMITED",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_ERROR",
    }
    return error_codes.get(status_code, "UNKNOWN_ERROR")


def _get_error_message(data: Any) -> str:
    """Extract a human-readable message from error data."""
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        # Get first error message
        for key, value in data.items():
            if isinstance(value, list) and value:
                return f"{key}: {value[0]}"
            if isinstance(value, str):
                return f"{key}: {value}"
    if isinstance(data, list) and data:
        return str(data[0])
    return "An error occurred"
