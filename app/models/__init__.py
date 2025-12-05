"""
Models package containing domain models, API schemas, and prompt builder.
"""
from app.models.domain import (
    DateFilter,
    AmountFilter,
    TextFilter,
    CodeLevel,
    PSCInfo,
    NAICSInfo,
    SetAsideFilter,
    FilterGroup,
    ProcurementQueryExtraction
)
from app.models.schemas import ExtractionRequest, ExtractionResponse, HealthResponse
from app.models.prompt_builder import build_system_prompt, build_user_prompt

__all__ = [
    # Domain models
    "DateFilter",
    "AmountFilter",
    "TextFilter",
    "CodeLevel",
    "PSCInfo",
    "NAICSInfo",
    "SetAsideFilter",
    "FilterGroup",
    "ProcurementQueryExtraction",
    # API schemas
    "ExtractionRequest",
    "ExtractionResponse",
    "HealthResponse",
    # Prompt builder
    "build_system_prompt",
    "build_user_prompt"
]
