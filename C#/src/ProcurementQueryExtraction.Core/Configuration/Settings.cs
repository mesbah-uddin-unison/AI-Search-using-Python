namespace ProcurementQueryExtraction.Core.Configuration;

/// <summary>
/// Application settings loaded from environment variables or configuration.
/// </summary>
public class Settings
{
    /// <summary>
    /// Azure OpenAI endpoint URL.
    /// </summary>
    public required string AzureOpenAIEndpoint { get; set; }

    /// <summary>
    /// Azure OpenAI API key.
    /// </summary>
    public required string AzureOpenAIApiKey { get; set; }

    /// <summary>
    /// Azure OpenAI deployment name.
    /// </summary>
    public required string AzureOpenAIDeployment { get; set; }

    /// <summary>
    /// Azure OpenAI API version.
    /// </summary>
    public string AzureOpenAIApiVersion { get; set; } = "2024-12-01-preview";

    /// <summary>
    /// Temperature for extraction (0.0-1.0).
    /// </summary>
    public float ExtractionTemperature { get; set; } = 0.1f;

    /// <summary>
    /// Number of days to use for "recent" queries.
    /// </summary>
    public int RecentDays { get; set; } = 90;

    /// <summary>
    /// API version string.
    /// </summary>
    public string ApiVersion { get; set; } = "1.0.0";
}
