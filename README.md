# Procurement Query Extraction Utility

A Python utility that converts natural language questions about U.S. federal procurement contracts into structured query filters using Azure OpenAI. The structured output enables data engineers to generate SQL queries for procurement databases.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Output Structure](#output-structure)
- [Field Reference](#field-reference)
- [Example Queries](#example-queries)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Natural Language Processing**: Converts conversational queries into structured, machine-readable data
- **Filter Groups with OR/AND Logic**: Supports complex queries with multiple filter groups
- **PSC/NAICS Code Intelligence**: Automatically identifies relevant Product Service Codes and NAICS codes with top two hierarchical levels
- **Set-Aside Detection**: Recognizes small business set-aside categories
- **SQL-Compatible Operators**: Provides clear operators (`=`, `>`, `<`, `BETWEEN`, `LIKE`, `IN`) for downstream SQL generation
- **Azure OpenAI Integration**: Uses structured outputs with JSON Schema for reliable extraction
- **Streamlit UI**: Interactive web interface for testing queries
- **Retry Logic**: Automatic retry for improved reliability

---

## Project Structure

```
procurement-query-extraction/
├── .env                          # Environment variables (create from .env.example)
├── .env.example                  # Environment variable template
├── requirements.txt              # Python dependencies
├── main.py                       # Test script for batch query testing
│
├── app/                          # Backend application
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Settings and configuration
│   │   └── exceptions.py         # Custom exception classes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── domain.py             # Pydantic models for structured output
│   │   └── prompt_builder.py     # LLM prompt construction
│   └── services/
│       ├── __init__.py
│       └── extraction.py         # Main extraction service
│
├── frontend/                     # Frontend application
│   └── streamlit_app.py          # Streamlit web UI
│
└── output/                       # Test results (auto-generated)
    └── test_results_*.json
```

---

## Installation

### Prerequisites

- Python 3.9 or higher
- Azure OpenAI API access with a deployment that supports structured outputs

### Setup

1. **Clone the repository** and navigate to the project directory

2. **Create and activate a virtual environment**:

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   ```bash
   # Copy the example env file
   cp .env.example .env

   # Edit .env with your Azure OpenAI credentials
   ```

---

## Configuration

Create a `.env` file in the project root with the following variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | Your Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Yes | Your Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | Your model deployment name |
| `AZURE_OPENAI_API_VERSION` | No | API version (default: `2024-12-01-preview`) |
| `EXTRACTION_TEMPERATURE` | No | LLM temperature 0.0-1.0 (default: `0.1`) |
| `RECENT_DAYS` | No | Days for "recent" queries (default: `90`) |

---

## Usage

### Option 1: Streamlit Web UI (Recommended)

Launch the interactive web interface:

```bash
# From project root
venv\Scripts\streamlit.exe run frontend/streamlit_app.py
```

The UI provides:
- Text input for natural language queries
- Temperature adjustment slider
- Formatted display of extracted filters
- JSON output view

### Option 2: Python Script

```python
from app.services.extraction import get_extraction_service

# Get the extraction service
service = get_extraction_service()

# Extract structured data from a natural language query
query = "Show me IT contracts over $1M in FY 2024"
result = service.extract(query=query)

print(result)
```

### Option 3: Batch Testing

Run the test script to process multiple queries:

```bash
python main.py
```

Results are saved to `output/test_results_TIMESTAMP.json`

---

## Output Structure

The extraction service returns a structured dictionary with the following format:

### Top-Level Structure

```json
{
  "original_query": "Show me IT contracts over $1M in FY 2024",
  "group_operator_between_groups": null,
  "filter_groups": [
    {
      // Filter Group 1 (filters combined with AND logic)
    }
  ]
}
```

### Complete Example Output

```json
{
  "original_query": "IT services contracts above $2M in 2024",
  "group_operator_between_groups": null,
  "filter_groups": [
    {
      "date": {
        "operator": "BETWEEN",
        "value": null,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
      },
      "total_amount": {
        "operator": ">",
        "value": 2000000.0,
        "min_value": null,
        "max_value": null
      },
      "subdoctype": {
        "operator": "=",
        "value": "Contract",
        "values": null
      },
      "product_service_code": {
        "psc_code": null,
        "description": "IT services",
        "level1": {
          "code": "D",
          "description": "IT and Telecom Services"
        },
        "level2": {
          "code": "DA",
          "description": "Various IT Services"
        }
      },
      "industry_code": {
        "naics_code": null,
        "description": "IT services",
        "level1": {
          "code": "54",
          "description": "Professional, Scientific, and Technical Services"
        },
        "level2": {
          "code": "541",
          "description": "Professional, Scientific, and Technical Services"
        }
      }
    }
  ]
}
```

### OR Query Example (Multiple Filter Groups)

```json
{
  "original_query": "8(a) contracts over $10M OR under $1M in FY 2024",
  "group_operator_between_groups": "OR",
  "filter_groups": [
    {
      "date": { "operator": "BETWEEN", "start_date": "2023-10-01", "end_date": "2024-09-30" },
      "total_amount": { "operator": ">", "value": 10000000.0 },
      "subdoctype": { "operator": "=", "value": "Contract" },
      "set_aside": { "description": "Competitive 8(a)", "code": ["O"] }
    },
    {
      "date": { "operator": "BETWEEN", "start_date": "2023-10-01", "end_date": "2024-09-30" },
      "total_amount": { "operator": "<", "value": 1000000.0 },
      "subdoctype": { "operator": "=", "value": "Contract" },
      "set_aside": { "description": "Competitive 8(a)", "code": ["O"] }
    }
  ]
}
```

---

## Field Reference

### Root Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `original_query` | `string` | The original natural language query from the user |
| `group_operator_between_groups` | `"AND"` \| `"OR"` \| `null` | How multiple filter groups are combined. `null` for single group queries |
| `filter_groups` | `array` | List of filter groups. Each group's filters are combined with AND logic |

---

### Filter Group Fields

Each filter group can contain the following optional fields:

#### `date` - Date Filter

Filters procurement records by date.

| Field | Type | Description |
|-------|------|-------------|
| `operator` | `"="` \| `"<"` \| `">"` \| `"<="` \| `">="` \| `"BETWEEN"` | SQL comparison operator |
| `value` | `string` \| `null` | Single date in `YYYY-MM-DD` format (for `=`, `<`, `>`, `<=`, `>=`) |
| `start_date` | `string` \| `null` | Start date for `BETWEEN` operator |
| `end_date` | `string` \| `null` | End date for `BETWEEN` operator |
| `recent_days` | `integer` \| `null` | Number of days when query uses "recent", "recently", or "latest" |

**Example:**
```json
{
  "operator": "BETWEEN",
  "value": null,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "recent_days": null
}
```

---

#### `funded_amount` / `total_amount` - Amount Filters

Filters by obligated amount (`funded_amount`) or total planned amount (`total_amount`).

| Field | Type | Description |
|-------|------|-------------|
| `operator` | `"="` \| `">"` \| `"<"` \| `">="` \| `"<="` \| `"BETWEEN"` | SQL comparison operator |
| `value` | `number` \| `null` | Single amount value (for `=`, `<`, `>`, `<=`, `>=`) |
| `min_value` | `number` \| `null` | Minimum amount for `BETWEEN` operator |
| `max_value` | `number` \| `null` | Maximum amount for `BETWEEN` operator |

**Example:**
```json
{
  "operator": ">",
  "value": 1000000.0,
  "min_value": null,
  "max_value": null
}
```

---

#### `vendor` - Vendor/Contractor Filter

Filters by contractor or business name.

| Field | Type | Description |
|-------|------|-------------|
| `operator` | `"="` \| `"LIKE"` \| `"IN"` | SQL comparison operator |
| `value` | `string` \| `null` | Single value for `=` or `LIKE` (use `%` for wildcards) |
| `values` | `array[string]` \| `null` | List of values for `IN` operator |

**Example:**
```json
{
  "operator": "LIKE",
  "value": "%Lockheed%",
  "values": null
}
```

---

#### `subdoctype` - Document Type Filter

Filters by procurement vehicle type.

| Field | Type | Description |
|-------|------|-------------|
| `operator` | `"="` \| `"LIKE"` \| `"IN"` | SQL comparison operator |
| `value` | `string` \| `null` | Single value for `=` or `LIKE` |
| `values` | `array[string]` \| `null` | List of values for `IN` operator |

**Supported Values:**

| Main Types | Award Sub-types |
|------------|-----------------|
| `awards` | `Contract`, `Delivery/Task Order`, `TDD`, `Work Assignment` |
| `solicitations` | `Other Transaction`, `BPA`, `BPA call`, `IAA` |
| `requisitions` | `Purchase Order`, `Purchase Card Order` |
| `funding opportunities` | `Multiple Award Setup`, `OT Delivery/Task Order` |
| `assistance agreements/grants` | |

**Example:**
```json
{
  "operator": "=",
  "value": "Contract",
  "values": null
}
```

---

#### `product_service_code` - PSC Information

Product Service Code filter with hierarchical categorization.

| Field | Type | Description |
|-------|------|-------------|
| `psc_code` | `array[string]` \| `null` | List of 4-character PSC codes (only when explicitly provided) |
| `description` | `string` \| `null` | Plain-language description from user query |
| `level1` | `object` \| `null` | PSC Level 1 category (1-character code) |
| `level2` | `object` \| `null` | PSC Level 2 subcategory (2-character code) |

**Level Object Structure:**
```json
{
  "code": "D",
  "description": "IT and Telecom Services"
}
```

**Example (description-based):**
```json
{
  "psc_code": null,
  "description": "IT services",
  "level1": { "code": "D", "description": "IT and Telecom Services" },
  "level2": { "code": "DA", "description": "Various IT Services" }
}
```

**Example (code-based):**
```json
{
  "psc_code": ["D308", "D310"],
  "description": null,
  "level1": null,
  "level2": null
}
```

**Common PSC Level 1 Categories:**

| Code | Description |
|------|-------------|
| `D` | IT and Telecom Services |
| `R` | Support Services (Professional, Administrative, Management) |
| `J` | Maintenance, Repair, and Rebuilding of Equipment |
| `Y` | Construction of Structures and Facilities |
| `Z` | Maintenance, Repair or Alteration of Real Property |
| `Q` | Medical Services |

---

#### `industry_code` - NAICS Information

North American Industry Classification System filter with hierarchical categorization.

| Field | Type | Description |
|-------|------|-------------|
| `naics_code` | `array[string]` \| `null` | List of 6-digit NAICS codes (only when explicitly provided) |
| `description` | `string` \| `null` | Plain-language description from user query |
| `level1` | `object` \| `null` | NAICS Level 1 sector (2-digit code) |
| `level2` | `object` \| `null` | NAICS Level 2 subsector (3-digit code) |

**Example:**
```json
{
  "naics_code": null,
  "description": "IT services",
  "level1": { "code": "54", "description": "Professional, Scientific, and Technical Services" },
  "level2": { "code": "541", "description": "Professional, Scientific, and Technical Services" }
}
```

**Common NAICS Level 1 Sectors:**

| Code | Description |
|------|-------------|
| `23` | Construction |
| `31-33` | Manufacturing |
| `54` | Professional, Scientific, and Technical Services |
| `56` | Administrative and Support Services |
| `62` | Health Care and Social Assistance |
| `81` | Other Services |

---

#### `set_aside` - Set-Aside Filter

Small business set-aside designation filter.

| Field | Type | Description |
|-------|------|-------------|
| `description` | `string` \| `null` | Plain-language description of set-aside type |
| `code` | `array[string]` \| `null` | List of set-aside codes |

**Common Set-Aside Codes:**

| Code | Description |
|------|-------------|
| `SBA` | Total Small Business Set-Aside |
| `SBP` | Partial Small Business Set-Aside |
| `8A` | 8(a) Set-Aside |
| `8AN` | 8(a) Sole Source |
| `HZC` | HUBZone Set-Aside |
| `HZS` | HUBZone Sole Source |
| `SDVOSBC` | SDVOSB Set-Aside |
| `SDVOSBS` | SDVOSB Sole Source |
| `WOSB` | WOSB Set-Aside |
| `WOSBSS` | WOSB Sole Source |
| `EDWOSB` | EDWOSB Set-Aside |
| `EDWOSBSS` | EDWOSB Sole Source |

**Example:**
```json
{
  "description": "Competitive 8(a)",
  "code": ["8A"]
}
```

---

## Example Queries

### Simple Query

**Input:** `"Show me construction contracts over $500K in FY 2024"`

**Output:**
```json
{
  "original_query": "Show me construction contracts over $500K in FY 2024",
  "group_operator_between_groups": null,
  "filter_groups": [{
    "date": { "operator": "BETWEEN", "start_date": "2023-10-01", "end_date": "2024-09-30" },
    "total_amount": { "operator": ">", "value": 500000.0 },
    "subdoctype": { "operator": "=", "value": "Contract" },
    "product_service_code": {
      "psc_code": null,
      "description": "construction",
      "level1": { "code": "Y", "description": "Construction of Structures and Facilities" },
      "level2": { "code": "Y", "description": "Construction of Structures and Facilities" }
    },
    "industry_code": {
      "naics_code": null,
      "description": "construction",
      "level1": { "code": "23", "description": "Construction" },
      "level2": { "code": "236", "description": "Construction of Buildings" }
    }
  }]
}
```

### Query with Specific Codes

**Input:** `"Pull solicitations that reference PSC 7030 or 7050 for software licenses"`

**Output:**
```json
{
  "original_query": "Pull solicitations that reference PSC 7030 or 7050 for software licenses",
  "group_operator_between_groups": null,
  "filter_groups": [{
    "subdoctype": { "operator": "=", "value": "solicitations" },
    "product_service_code": {
      "psc_code": ["7030", "7050"],
      "description": "software licenses",
      "level1": { "code": "70", "description": "ADP Equipment, Software, Supplies" },
      "level2": { "code": "70", "description": "ADP Equipment, Software, Supplies" }
    }
  }]
}
```

### Complex OR Query

**Input:** `"8(a) contracts over $10M OR under $1M in FY 2024"`

**Output:**
```json
{
  "original_query": "8(a) contracts over $10M OR under $1M in FY 2024",
  "group_operator_between_groups": "OR",
  "filter_groups": [
    {
      "date": { "operator": "BETWEEN", "start_date": "2023-10-01", "end_date": "2024-09-30" },
      "total_amount": { "operator": ">", "value": 10000000.0 },
      "subdoctype": { "operator": "=", "value": "Contract" },
      "set_aside": { "description": "Competitive 8(a)", "code": ["O"] }
    },
    {
      "date": { "operator": "BETWEEN", "start_date": "2023-10-01", "end_date": "2024-09-30" },
      "total_amount": { "operator": "<", "value": 1000000.0 },
      "subdoctype": { "operator": "=", "value": "Contract" },
      "set_aside": { "description": "Competitive 8(a)", "code": ["O"] }
    }
  ]
}
```

---

## Troubleshooting

### Environment Variable Errors

Ensure all required environment variables are set in the `.env` file:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`

### API Version Compatibility

If you encounter API errors, ensure your Azure OpenAI deployment supports structured outputs (requires API version `2024-12-01-preview` or later).

### Validation Errors

The system automatically retries (up to 5 times) when validation errors occur. If errors persist:
1. Check that your query is clear and unambiguous
2. Try simplifying complex queries
3. Review the logs for specific error messages

### Import Errors

If running the Streamlit app fails with import errors:
```bash
# Ensure you're in the project root directory
cd "path/to/project"

# Run with the correct path
venv\Scripts\streamlit.exe run frontend/streamlit_app.py
```

---

## License

This utility is provided for federal procurement data processing purposes.

## Support

For issues or questions:
- Check the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- Review the error logs in the console output
- Contact your Azure support team for API-related issues
