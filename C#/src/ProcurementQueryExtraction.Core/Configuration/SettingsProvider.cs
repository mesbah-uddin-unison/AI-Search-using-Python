using Microsoft.Extensions.Configuration;

namespace ProcurementQueryExtraction.Core.Configuration;

/// <summary>
/// Provides settings from environment variables and configuration files.
/// </summary>
public static class SettingsProvider
{
    private static Settings? _cachedSettings;

    /// <summary>
    /// Gets the application settings.
    /// </summary>
    /// <param name="configuration">Optional configuration object. If null, reads from environment variables.</param>
    /// <returns>Application settings.</returns>
    /// <exception cref="InvalidOperationException">Thrown when required settings are missing.</exception>
    public static Settings GetSettings(IConfiguration? configuration = null)
    {
        if (_cachedSettings != null)
            return _cachedSettings;

        string? endpoint, apiKey, deployment, apiVersion;

        if (configuration != null)
        {
            // Read from IConfiguration (supports appsettings.json, user secrets, env vars)
            endpoint = configuration["AZURE_OPENAI_ENDPOINT"];
            apiKey = configuration["AZURE_OPENAI_API_KEY"];
            deployment = configuration["AZURE_OPENAI_DEPLOYMENT"];
            apiVersion = configuration["AZURE_OPENAI_API_VERSION"];
        }
        else
        {
            // Read directly from environment variables
            endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT");
            apiKey = Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY");
            deployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT");
            apiVersion = Environment.GetEnvironmentVariable("AZURE_OPENAI_API_VERSION");
        }

        // Validate required settings
        if (string.IsNullOrEmpty(endpoint))
            throw new InvalidOperationException("AZURE_OPENAI_ENDPOINT is required but not set.");
        if (string.IsNullOrEmpty(apiKey))
            throw new InvalidOperationException("AZURE_OPENAI_API_KEY is required but not set.");
        if (string.IsNullOrEmpty(deployment))
            throw new InvalidOperationException("AZURE_OPENAI_DEPLOYMENT is required but not set.");

        _cachedSettings = new Settings
        {
            AzureOpenAIEndpoint = endpoint,
            AzureOpenAIApiKey = apiKey,
            AzureOpenAIDeployment = deployment,
            AzureOpenAIApiVersion = apiVersion ?? "2024-12-01-preview"
        };

        // Read optional settings
        var tempStr = configuration?["EXTRACTION_TEMPERATURE"]
            ?? Environment.GetEnvironmentVariable("EXTRACTION_TEMPERATURE");
        if (float.TryParse(tempStr, out var temp))
            _cachedSettings.ExtractionTemperature = temp;

        var recentStr = configuration?["RECENT_DAYS"]
            ?? Environment.GetEnvironmentVariable("RECENT_DAYS");
        if (int.TryParse(recentStr, out var recent))
            _cachedSettings.RecentDays = recent;

        return _cachedSettings;
    }

    /// <summary>
    /// Clears the cached settings (useful for testing).
    /// </summary>
    public static void ClearCache()
    {
        _cachedSettings = null;
    }
}
