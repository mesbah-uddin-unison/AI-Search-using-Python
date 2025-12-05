"""
FastAPI application entry point for the Procurement Query Extraction API.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.config import get_settings
from app.core.exceptions import (
    ExtractionError,
    AzureOpenAIError,
    ValidationError,
    extraction_error_handler,
    azure_openai_error_handler,
    validation_error_handler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()

    app = FastAPI(
        title="Procurement Query Extraction API",
        description="API for extracting structured filters from natural language procurement queries",
        version=settings.api_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    app.add_exception_handler(ExtractionError, extraction_error_handler)
    app.add_exception_handler(AzureOpenAIError, azure_openai_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)

    # Include API routes
    app.include_router(api_router, prefix="/api/v1", tags=["extraction"])

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting Procurement Query Extraction API")
        logger.info(f"API Version: {settings.api_version}")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down Procurement Query Extraction API")

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
