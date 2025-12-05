"""
API request and response schemas for the extraction API.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    """Request schema for the extraction endpoint."""

    query: str = Field(
        ...,
        description="Natural language query about U.S. federal procurement contracts",
        min_length=1,
        max_length=2000
    )
    temperature: Optional[float] = Field(
        None,
        description="Temperature for LLM extraction (0.0-1.0). Lower = more deterministic.",
        ge=0.0,
        le=1.0
    )


class ExtractionResponse(BaseModel):
    """Response schema for the extraction endpoint."""

    success: bool = Field(
        description="Whether the extraction was successful"
    )
    data: Optional[dict] = Field(
        None,
        description="The extracted structured data (filter groups, operators, etc.)"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if the extraction failed"
    )
    details: Optional[str] = Field(
        None,
        description="Additional error details if available"
    )


class HealthResponse(BaseModel):
    """Response schema for the health check endpoint."""

    status: str = Field(
        description="Health status of the API"
    )
    version: str = Field(
        description="API version"
    )
