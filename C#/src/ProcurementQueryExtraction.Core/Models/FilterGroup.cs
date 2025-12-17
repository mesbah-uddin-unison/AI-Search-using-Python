using System.Text.Json.Serialization;

namespace ProcurementQueryExtraction.Core.Models;

/// <summary>
/// A group of filters combined with AND logic internally.
/// </summary>
public class FilterGroup
{
    /// <summary>
    /// Filter for when the work/contract began (Period of Performance Start).
    /// </summary>
    [JsonPropertyName("StartDate")]
    public DateFilter? StartDate { get; set; }

    /// <summary>
    /// Filter for when the work/contract ended (Period of Performance End).
    /// </summary>
    [JsonPropertyName("EndDate")]
    public DateFilter? EndDate { get; set; }

    /// <summary>
    /// Filter for the obligated amount.
    /// </summary>
    [JsonPropertyName("funded_amount")]
    public AmountFilter? FundedAmount { get; set; }

    /// <summary>
    /// Filter for the total planned amount.
    /// </summary>
    [JsonPropertyName("total_amount")]
    public AmountFilter? TotalAmount { get; set; }

    /// <summary>
    /// Filter for contractor/vendor name.
    /// </summary>
    [JsonPropertyName("vendor")]
    public TextFilter? Vendor { get; set; }

    /// <summary>
    /// Filter for vehicle type (awards, solicitations, etc.).
    /// </summary>
    [JsonPropertyName("subdoctype")]
    public TextFilter? Subdoctype { get; set; }

    /// <summary>
    /// Product Service Code (PSC) filter including codes, description, and category levels.
    /// </summary>
    [JsonPropertyName("product_service_code")]
    public PSCInfo? ProductServiceCode { get; set; }

    /// <summary>
    /// Industry Code (NAICS) filter including codes, description, and sector levels.
    /// </summary>
    [JsonPropertyName("industry_code")]
    public NAICSInfo? IndustryCode { get; set; }

    /// <summary>
    /// Set-aside filter with description and code(s).
    /// </summary>
    [JsonPropertyName("set_aside")]
    public SetAsideFilter? SetAside { get; set; }
}
