using System.Text.Json.Serialization;

namespace ProcurementQueryExtraction.Core.Models;

/// <summary>
/// Date range filter with SQL-compatible operator support.
/// </summary>
public class DateFilter
{
    /// <summary>
    /// SQL comparison operator for date filtering.
    /// </summary>
    [JsonPropertyName("operator")]
    public required string Operator { get; set; }

    /// <summary>
    /// Single date value in YYYY-MM-DD format for =/</>/<=/>=  operators.
    /// </summary>
    [JsonPropertyName("value")]
    public string? Value { get; set; }

    /// <summary>
    /// Start date for 'BETWEEN' operator in YYYY-MM-DD format.
    /// </summary>
    [JsonPropertyName("start_date")]
    public string? StartDate { get; set; }

    /// <summary>
    /// End date for 'BETWEEN' operator in YYYY-MM-DD format.
    /// </summary>
    [JsonPropertyName("end_date")]
    public string? EndDate { get; set; }

    /// <summary>
    /// Number of days used for 'recent' date calculation.
    /// Only populated when query uses 'recent', 'recently', or 'latest' keywords.
    /// </summary>
    [JsonPropertyName("recent_days")]
    public int? RecentDays { get; set; }
}

/// <summary>
/// Amount filter with SQL-compatible operator support.
/// </summary>
public class AmountFilter
{
    /// <summary>
    /// SQL comparison operator for amount filtering.
    /// </summary>
    [JsonPropertyName("operator")]
    public required string Operator { get; set; }

    /// <summary>
    /// Single amount value for =/>/</>=/<=  operators.
    /// </summary>
    [JsonPropertyName("value")]
    public double? Value { get; set; }

    /// <summary>
    /// Minimum amount for 'BETWEEN' operator.
    /// </summary>
    [JsonPropertyName("min_value")]
    public double? MinValue { get; set; }

    /// <summary>
    /// Maximum amount for 'BETWEEN' operator.
    /// </summary>
    [JsonPropertyName("max_value")]
    public double? MaxValue { get; set; }
}

/// <summary>
/// Text field filter with SQL-compatible operator support.
/// </summary>
public class TextFilter
{
    /// <summary>
    /// SQL comparison operator for text filtering (= for exact match, LIKE for pattern match, IN for list).
    /// </summary>
    [JsonPropertyName("operator")]
    public required string Operator { get; set; }

    /// <summary>
    /// Single text value for = or LIKE operators.
    /// </summary>
    [JsonPropertyName("value")]
    public string? Value { get; set; }

    /// <summary>
    /// List of values for 'IN' operator.
    /// </summary>
    [JsonPropertyName("values")]
    public List<string>? Values { get; set; }
}

/// <summary>
/// Code level with code and description (used for PSC/NAICS levels).
/// </summary>
public class CodeLevel
{
    /// <summary>
    /// The code value.
    /// </summary>
    [JsonPropertyName("code")]
    public required string Code { get; set; }

    /// <summary>
    /// Description of the code.
    /// </summary>
    [JsonPropertyName("description")]
    public required string Description { get; set; }
}

/// <summary>
/// Consolidated PSC information with code, description, and levels.
/// </summary>
public class PSCInfo
{
    /// <summary>
    /// List of PSC codes to filter by.
    /// </summary>
    [JsonPropertyName("psc_code")]
    public List<string>? PscCode { get; set; }

    /// <summary>
    /// Plain-language description of Product Service Code category from user request.
    /// </summary>
    [JsonPropertyName("description")]
    public string? Description { get; set; }

    /// <summary>
    /// PSC Level 1 (1-character category code).
    /// </summary>
    [JsonPropertyName("level1")]
    public CodeLevel? Level1 { get; set; }

    /// <summary>
    /// PSC Level 2 (2-character subcategory code).
    /// </summary>
    [JsonPropertyName("level2")]
    public CodeLevel? Level2 { get; set; }
}

/// <summary>
/// Consolidated NAICS information with code, description, and levels.
/// </summary>
public class NAICSInfo
{
    /// <summary>
    /// List of NAICS codes to filter by.
    /// </summary>
    [JsonPropertyName("naics_code")]
    public List<string>? NaicsCode { get; set; }

    /// <summary>
    /// Plain-language description of NAICS category from user request.
    /// </summary>
    [JsonPropertyName("description")]
    public string? Description { get; set; }

    /// <summary>
    /// NAICS Level 1 (2-digit sector code).
    /// </summary>
    [JsonPropertyName("level1")]
    public CodeLevel? Level1 { get; set; }

    /// <summary>
    /// NAICS Level 2 (3-digit subsector code).
    /// </summary>
    [JsonPropertyName("level2")]
    public CodeLevel? Level2 { get; set; }
}

/// <summary>
/// Set-aside filter with description and code.
/// </summary>
public class SetAsideFilter
{
    /// <summary>
    /// Plain-language description of set-aside category (e.g., 'Total Small Business', 'HUBZone').
    /// </summary>
    [JsonPropertyName("description")]
    public string? Description { get; set; }

    /// <summary>
    /// List of set-aside codes to filter by (e.g., ['C', 'E'] for Small Business and HUBZone).
    /// </summary>
    [JsonPropertyName("code")]
    public List<string>? Code { get; set; }
}
