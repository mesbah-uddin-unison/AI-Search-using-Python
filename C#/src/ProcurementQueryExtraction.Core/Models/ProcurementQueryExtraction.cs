using System.Text.Json.Serialization;

namespace ProcurementQueryExtraction.Core.Models;

/// <summary>
/// Structured extraction of procurement contract query.
/// </summary>
public class ProcurementQueryExtraction
{
    /// <summary>
    /// List of filter groups. Single group for simple AND queries, multiple groups for OR queries.
    /// </summary>
    [JsonPropertyName("filter_groups")]
    public required List<FilterGroup> FilterGroups { get; set; }

    /// <summary>
    /// How filter_groups are combined. Only required when there are multiple groups.
    /// Use 'OR' for OR logic between groups, 'AND' for AND logic. Leave null for single group queries.
    /// </summary>
    [JsonPropertyName("group_operator_between_groups")]
    public string? GroupOperatorBetweenGroups { get; set; }

    /// <summary>
    /// The original natural language query from the user.
    /// </summary>
    [JsonPropertyName("original_query")]
    public required string OriginalQuery { get; set; }
}
