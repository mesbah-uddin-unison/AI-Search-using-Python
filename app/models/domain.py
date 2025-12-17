"""
Pydantic models for structured procurement contract query extraction.
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict


class DateFilter(BaseModel):
    """Date range filter with SQL-compatible operator support."""
    model_config = ConfigDict(extra='forbid')

    operator: Literal["=", "<", ">", "<=", ">=", "BETWEEN"] = Field(
        description="SQL comparison operator for date filtering"
    )
    value: Optional[str] = Field(
        None,
        description="Single date value in YYYY-MM-DD format for =/</>/<=/>=  operators"
    )
    start_date: Optional[str] = Field(
        None,
        description="Start date for 'BETWEEN' operator in YYYY-MM-DD format"
    )
    end_date: Optional[str] = Field(
        None,
        description="End date for 'BETWEEN' operator in YYYY-MM-DD format"
    )
    recent_days: Optional[int] = Field(
        None,
        description="Number of days used for 'recent' date calculation. Only populated when query uses 'recent', 'recently', or 'latest' keywords."
    )


class AmountFilter(BaseModel):
    """Amount filter with SQL-compatible operator support."""
    model_config = ConfigDict(extra='forbid')

    operator: Literal["=", ">", "<", ">=", "<=", "BETWEEN"] = Field(
        description="SQL comparison operator for amount filtering"
    )
    value: Optional[float] = Field(
        None,
        description="Single amount value for =/>/</>=/<=  operators"
    )
    min_value: Optional[float] = Field(
        None,
        description="Minimum amount for 'BETWEEN' operator"
    )
    max_value: Optional[float] = Field(
        None,
        description="Maximum amount for 'BETWEEN' operator"
    )


class TextFilter(BaseModel):
    """Text field filter with SQL-compatible operator support."""
    model_config = ConfigDict(extra='forbid')

    operator: Literal["=", "LIKE", "IN"] = Field(
        description="SQL comparison operator for text filtering (= for exact match, LIKE for pattern match, IN for list)"
    )
    value: Optional[str] = Field(
        None,
        description="Single text value for = or LIKE operators"
    )
    values: Optional[List[str]] = Field(
        None,
        description="List of values for 'IN' operator"
    )


class CodeLevel(BaseModel):
    """Code level with code and description (used for PSC/NAICS levels)."""
    model_config = ConfigDict(extra='forbid')

    code: str = Field(description="The code value")
    description: str = Field(description="Description of the code")


class PSCInfo(BaseModel):
    """Consolidated PSC information with code, description, and levels."""
    model_config = ConfigDict(extra='forbid')

    psc_code: Optional[List[str]] = Field(
        None,
        description="List of PSC codes to filter by"
    )
    description: Optional[str] = Field(
        None,
        description="Plain-language description of Product Service Code category from user request"
    )
    level1: Optional[CodeLevel] = Field(
        None,
        description="PSC Level 1 (1-character category code)"
    )
    level2: Optional[CodeLevel] = Field(
        None,
        description="PSC Level 2 (2-character subcategory code)"
    )


class NAICSInfo(BaseModel):
    """Consolidated NAICS information with code, description, and levels."""
    model_config = ConfigDict(extra='forbid')

    naics_code: Optional[List[str]] = Field(
        None,
        description="List of NAICS codes to filter by"
    )
    description: Optional[str] = Field(
        None,
        description="Plain-language description of NAICS category from user request"
    )
    level1: Optional[CodeLevel] = Field(
        None,
        description="NAICS Level 1 (2-digit sector code)"
    )
    level2: Optional[CodeLevel] = Field(
        None,
        description="NAICS Level 2 (3-digit subsector code)"
    )


class SetAsideFilter(BaseModel):
    """Set-aside filter with description and code."""
    model_config = ConfigDict(extra='forbid')

    description: Optional[str] = Field(
        None,
        description="Plain-language description of set-aside category (e.g., 'Total Small Business', 'HUBZone')"
    )
    code: Optional[List[str]] = Field(
        None,
        description="List of set-aside codes to filter by (e.g., ['C', 'E'] for Small Business and HUBZone)"
    )


class FilterGroup(BaseModel):
    """A group of filters combined with AND logic internally."""
    model_config = ConfigDict(extra='forbid')

    # Date fields - StartDate and EndDate for Period of Performance
    StartDate: Optional[DateFilter] = Field(
        None,
        description="Filter for when the work/contract began (Period of Performance Start)"
    )
    EndDate: Optional[DateFilter] = Field(
        None,
        description="Filter for when the work/contract ended (Period of Performance End)"
    )

    # Amount fields
    funded_amount: Optional[AmountFilter] = Field(
        None,
        description="Filter for the obligated amount"
    )
    total_amount: Optional[AmountFilter] = Field(
        None,
        description="Filter for the total planned amount"
    )

    # Text fields
    vendor: Optional[TextFilter] = Field(
        None,
        description="Filter for contractor/vendor name"
    )
    subdoctype: Optional[TextFilter] = Field(
        None,
        description="Filter for vehicle type (awards, solicitations, etc.)"
    )

    # PSC information (code, description, levels) - renamed to be more distinct
    product_service_code: Optional[PSCInfo] = Field(
        None,
        description="Product Service Code (PSC) filter including codes, description, and category levels"
    )

    # NAICS information (code, description, levels) - renamed to be more distinct
    industry_code: Optional[NAICSInfo] = Field(
        None,
        description="Industry Code (NAICS) filter including codes, description, and sector levels"
    )

    # Set-aside filter (description + code)
    set_aside: Optional[SetAsideFilter] = Field(
        None,
        description="Set-aside filter with description and code(s)"
    )


class ProcurementQueryExtraction(BaseModel):
    """Structured extraction of procurement contract query."""
    model_config = ConfigDict(extra='forbid')

    # Filter groups (required - always at least one group)
    filter_groups: List[FilterGroup] = Field(
        description="List of filter groups. Single group for simple AND queries, multiple groups for OR queries."
    )
    group_operator_between_groups: Optional[Literal["AND", "OR"]] = Field(
        None,
        description="How filter_groups are combined. Only required when there are multiple groups. Use 'OR' for OR logic between groups, 'AND' for AND logic. Leave null for single group queries."
    )

    # Original query for reference
    original_query: str = Field(
        description="The original natural language query from the user"
    )
