"""
Custom exceptions for the extraction API.
"""
from fastapi import Request
from fastapi.responses import JSONResponse


class ExtractionError(Exception):
    """Base exception for extraction errors."""

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class AzureOpenAIError(ExtractionError):
    """Exception for Azure OpenAI API errors."""

    def __init__(self, message: str, details: str = None):
        super().__init__(f"Azure OpenAI Error: {message}", details)


class ValidationError(ExtractionError):
    """Exception for validation errors."""

    def __init__(self, message: str, details: str = None):
        super().__init__(f"Validation Error: {message}", details)


async def extraction_error_handler(request: Request, exc: ExtractionError) -> JSONResponse:
    """
    Handle ExtractionError exceptions.

    Args:
        request: FastAPI request object
        exc: ExtractionError exception

    Returns:
        JSONResponse with error details
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": exc.message,
            "details": exc.details
        }
    )


async def azure_openai_error_handler(request: Request, exc: AzureOpenAIError) -> JSONResponse:
    """
    Handle AzureOpenAIError exceptions.

    Args:
        request: FastAPI request object
        exc: AzureOpenAIError exception

    Returns:
        JSONResponse with error details
    """
    return JSONResponse(
        status_code=503,
        content={
            "success": False,
            "data": None,
            "error": exc.message,
            "details": exc.details
        }
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle ValidationError exceptions.

    Args:
        request: FastAPI request object
        exc: ValidationError exception

    Returns:
        JSONResponse with error details
    """
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "data": None,
            "error": exc.message,
            "details": exc.details
        }
    )
