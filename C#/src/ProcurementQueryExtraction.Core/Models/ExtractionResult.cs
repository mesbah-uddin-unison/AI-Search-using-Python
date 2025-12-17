using System.Text.Json.Serialization;

namespace ProcurementQueryExtraction.Core.Models;

/// <summary>
/// Result of the extraction process, containing the structured data as a dictionary.
/// </summary>
public class ExtractionResult
{
    /// <summary>
    /// The original natural language query.
    /// </summary>
    [JsonPropertyName("original_query")]
    public required string OriginalQuery { get; set; }

    /// <summary>
    /// List of filter groups converted to dictionary format.
    /// </summary>
    [JsonPropertyName("filter_groups")]
    public required List<Dictionary<string, object?>> FilterGroups { get; set; }

    /// <summary>
    /// Operator between filter groups (AND/OR).
    /// </summary>
    [JsonPropertyName("group_operator_between_groups")]
    public string? GroupOperatorBetweenGroups { get; set; }
}
