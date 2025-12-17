"""
Extraction service for converting natural language queries to structured output.
"""
import logging
from typing import Optional, Dict, Any
from openai import AzureOpenAI

from app.core.config import get_settings
from app.core.exceptions import AzureOpenAIError, ExtractionError
from app.models.domain import ProcurementQueryExtraction, FilterGroup
from app.models.prompt_builder import build_system_prompt, build_user_prompt

logger = logging.getLogger(__name__)


class ExtractionService:
    """Service for extracting structured data from natural language queries."""

    def __init__(self):
        """Initialize the extraction service."""
        self._client: Optional[AzureOpenAI] = None
        self._deployment: Optional[str] = None

    def _get_client(self) -> tuple[AzureOpenAI, str]:
        """
        Get or create the Azure OpenAI client.

        Returns:
            Tuple of (AzureOpenAI client, deployment name)
        """
        if self._client is None:
            settings = get_settings()
            self._client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
            )
            self._deployment = settings.azure_openai_deployment
            logger.info("Azure OpenAI client initialized")
        return self._client, self._deployment

    def extract(
        self,
        query: str,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Extract structured procurement query data from natural language.

        Args:
            query: Natural language question about procurement contracts
            temperature: Temperature for LLM (0.0-1.0). If None, uses default from settings.

        Returns:
            Dictionary with extracted structured data

        Raises:
            AzureOpenAIError: If Azure OpenAI API call fails
            ExtractionError: If extraction or validation fails
        """
        settings = get_settings()
        if temperature is None:
            temperature = settings.extraction_temperature

        logger.info(f"Processing extraction query: {query[:100]}...")

        max_retries = 5
        last_error = None

        for attempt in range(max_retries):
            # Slightly vary temperature on retries to get different outputs
            retry_temperature = temperature + (attempt * 0.05) if attempt > 0 else temperature
            try:
                client, deployment = self._get_client()

                # Build prompts
                system_prompt = build_system_prompt(recent_days=settings.recent_days)
                user_prompt = build_user_prompt(query)

                logger.debug(f"Calling Azure OpenAI API (attempt {attempt + 1}/{max_retries})")

                # Call Azure OpenAI with structured output
                # Note: strict mode is not used because it requires all properties in 'required',
                # which is incompatible with optional fields in our schema
                response = client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=retry_temperature,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "procurement_query_extraction",
                            "description": "Structured extraction of procurement contract query",
                            "schema": ProcurementQueryExtraction.model_json_schema()
                        }
                    }
                )

                # Parse response
                response_content = response.choices[0].message.content
                logger.debug("Received response from Azure OpenAI")

                # Validate and parse as Pydantic model
                extraction = ProcurementQueryExtraction.model_validate_json(response_content)
                logger.info(f"Extraction successful on attempt {attempt + 1}: {len(extraction.filter_groups)} filter group(s)")

                # Convert to dictionary format
                result = self._extraction_to_dict(extraction)
                return result

            except Exception as e:
                last_error = e
                error_msg = str(e)
                # If it's a validation error (likely bad nesting), retry
                if "extra_forbidden" in error_msg or "Extra inputs are not permitted" in error_msg:
                    logger.warning(f"Validation error on attempt {attempt + 1}, retrying: {error_msg}")
                    continue
                # For other errors, don't retry
                break

        # All retries failed
        if last_error:
            e = last_error
            error_msg = str(e)
            if "openai" in error_msg.lower() or "api" in error_msg.lower():
                logger.error(f"Azure OpenAI API error: {error_msg}")
                raise AzureOpenAIError(error_msg)
            else:
                logger.error(f"Extraction error: {error_msg}")
                raise ExtractionError("Failed to extract query", error_msg)

    def _extraction_to_dict(self, extraction: ProcurementQueryExtraction) -> Dict[str, Any]:
        """
        Convert extraction to a dictionary format.

        Args:
            extraction: ProcurementQueryExtraction object

        Returns:
            Dictionary with structured filter groups
        """
        result = {
            "original_query": extraction.original_query,
            "group_operator_between_groups": extraction.group_operator_between_groups,
            "filter_groups": []
        }

        for group in extraction.filter_groups:
            group_dict = self._convert_filter_group(group)
            result["filter_groups"].append(group_dict)

        return result

    def _convert_filter_group(self, group: FilterGroup) -> Dict[str, Any]:
        """
        Convert a FilterGroup model to a dictionary.

        Args:
            group: FilterGroup object

        Returns:
            Dictionary representation of the filter group
        """
        group_dict = {}

        # StartDate filter (Period of Performance Start)
        if group.StartDate:
            start_date_filter = {
                "operator": group.StartDate.operator,
                "value": group.StartDate.value,
                "start_date": group.StartDate.start_date,
                "end_date": group.StartDate.end_date
            }
            if group.StartDate.recent_days:
                start_date_filter["recent_days"] = group.StartDate.recent_days
            group_dict["StartDate"] = start_date_filter

        # EndDate filter (Period of Performance End)
        if group.EndDate:
            end_date_filter = {
                "operator": group.EndDate.operator,
                "value": group.EndDate.value,
                "start_date": group.EndDate.start_date,
                "end_date": group.EndDate.end_date
            }
            if group.EndDate.recent_days:
                end_date_filter["recent_days"] = group.EndDate.recent_days
            group_dict["EndDate"] = end_date_filter

        # Amount filters
        if group.funded_amount:
            group_dict["funded_amount"] = {
                "operator": group.funded_amount.operator,
                "value": group.funded_amount.value,
                "min_value": group.funded_amount.min_value,
                "max_value": group.funded_amount.max_value
            }

        if group.total_amount:
            group_dict["total_amount"] = {
                "operator": group.total_amount.operator,
                "value": group.total_amount.value,
                "min_value": group.total_amount.min_value,
                "max_value": group.total_amount.max_value
            }

        # Text filters
        if group.subdoctype:
            group_dict["subdoctype"] = {
                "operator": group.subdoctype.operator,
                "value": group.subdoctype.value,
                "values": group.subdoctype.values
            }

        if group.vendor:
            group_dict["vendor"] = {
                "operator": group.vendor.operator,
                "value": group.vendor.value,
                "values": group.vendor.values
            }

        # PSC info (code, description, levels) - now called product_service_code
        if group.product_service_code:
            group_dict["product_service_code"] = {
                "psc_code": group.product_service_code.psc_code,
                "description": group.product_service_code.description,
                "level1": group.product_service_code.level1.model_dump() if group.product_service_code.level1 else None,
                "level2": group.product_service_code.level2.model_dump() if group.product_service_code.level2 else None
            }

        # NAICS info (code, description, levels) - now called industry_code
        if group.industry_code:
            group_dict["industry_code"] = {
                "naics_code": group.industry_code.naics_code,
                "description": group.industry_code.description,
                "level1": group.industry_code.level1.model_dump() if group.industry_code.level1 else None,
                "level2": group.industry_code.level2.model_dump() if group.industry_code.level2 else None
            }

        # Set-aside filter (description + code)
        if group.set_aside:
            group_dict["set_aside"] = {
                "description": group.set_aside.description,
                "code": group.set_aside.code
            }

        return group_dict


# Singleton instance for dependency injection
_extraction_service: Optional[ExtractionService] = None


def get_extraction_service() -> ExtractionService:
    """
    Get the extraction service instance.

    Returns:
        ExtractionService singleton instance
    """
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ExtractionService()
    return _extraction_service
