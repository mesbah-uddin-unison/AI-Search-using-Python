"""
API routes for the extraction service.
"""
import logging
from fastapi import APIRouter, Depends

from app.core.config import get_settings, Settings
from app.core.exceptions import ExtractionError, AzureOpenAIError
from app.models.schemas import ExtractionRequest, ExtractionResponse, HealthResponse
from app.services.extraction import get_extraction_service, ExtractionService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/extract", response_model=ExtractionResponse)
async def extract_query(
    request: ExtractionRequest,
    service: ExtractionService = Depends(get_extraction_service)
) -> ExtractionResponse:
    """
    Extract structured filters from a natural language procurement query.

    Args:
        request: The extraction request containing the query
        service: The extraction service (injected)

    Returns:
        ExtractionResponse with extracted data or error
    """
    logger.info(f"Received extraction request: {request.query[:50]}...")

    try:
        result = service.extract(
            query=request.query,
            temperature=request.temperature
        )

        return ExtractionResponse(
            success=True,
            data=result,
            error=None,
            details=None
        )

    except AzureOpenAIError as e:
        logger.error(f"Azure OpenAI error: {e.message}")
        return ExtractionResponse(
            success=False,
            data=None,
            error=e.message,
            details=e.details
        )

    except ExtractionError as e:
        logger.error(f"Extraction error: {e.message}")
        return ExtractionResponse(
            success=False,
            data=None,
            error=e.message,
            details=e.details
        )

    except Exception as e:
        logger.exception("Unexpected error during extraction")
        return ExtractionResponse(
            success=False,
            data=None,
            error="An unexpected error occurred",
            details=str(e)
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_settings)
) -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse with status and version
    """
    return HealthResponse(
        status="healthy",
        version=settings.api_version
    )
