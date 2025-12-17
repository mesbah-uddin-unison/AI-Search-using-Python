using System.ClientModel;
using System.Text.Json;
using Azure;
using Azure.AI.OpenAI;
using Microsoft.Extensions.Logging;
using OpenAI.Chat;
using ProcurementQueryExtraction.Core.Configuration;
using ProcurementQueryExtraction.Core.Models;

namespace ProcurementQueryExtraction.Core.Services;

/// <summary>
/// Custom exception for Azure OpenAI API errors.
/// </summary>
public class AzureOpenAIException : Exception
{
    public AzureOpenAIException(string message) : base(message) { }
    public AzureOpenAIException(string message, Exception inner) : base(message, inner) { }
}

/// <summary>
/// Custom exception for extraction errors.
/// </summary>
public class ExtractionException : Exception
{
    public string? Details { get; }
    public ExtractionException(string message, string? details = null) : base(message)
    {
        Details = details;
    }
}

/// <summary>
/// Service for extracting structured procurement query data using Azure OpenAI.
/// </summary>
public class ExtractionService
{
    private readonly Settings _settings;
    private readonly ILogger<ExtractionService>? _logger;
    private AzureOpenAIClient? _client;
    private ChatClient? _chatClient;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        WriteIndented = false,
        DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
    };

    /// <summary>
    /// Initializes a new instance of the ExtractionService.
    /// </summary>
    /// <param name="settings">Application settings. If null, loads from environment.</param>
    /// <param name="logger">Optional logger.</param>
    public ExtractionService(Settings? settings = null, ILogger<ExtractionService>? logger = null)
    {
        _settings = settings ?? SettingsProvider.GetSettings();
        _logger = logger;
    }

    /// <summary>
    /// Gets or creates the Azure OpenAI client.
    /// </summary>
    private (AzureOpenAIClient Client, ChatClient ChatClient) GetClient()
    {
        if (_client == null || _chatClient == null)
        {
            _client = new AzureOpenAIClient(
                new Uri(_settings.AzureOpenAIEndpoint),
                new AzureKeyCredential(_settings.AzureOpenAIApiKey));

            _chatClient = _client.GetChatClient(_settings.AzureOpenAIDeployment);
        }
        return (_client, _chatClient);
    }

    /// <summary>
    /// Extracts structured procurement query data from a natural language query.
    /// </summary>
    /// <param name="query">The natural language query.</param>
    /// <param name="temperature">Optional temperature override.</param>
    /// <returns>Dictionary containing the extraction result.</returns>
    public async Task<Dictionary<string, object?>> ExtractAsync(string query, float? temperature = null)
    {
        temperature ??= _settings.ExtractionTemperature;

        _logger?.LogInformation("Processing extraction query: {Query}", query.Length > 100 ? query[..100] + "..." : query);

        const int maxRetries = 5;
        Exception? lastError = null;

        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            // Slightly vary temperature on retries to get different outputs
            var retryTemperature = attempt > 0 ? temperature.Value + (attempt * 0.05f) : temperature.Value;

            try
            {
                var (_, chatClient) = GetClient();

                // Build prompts
                var systemPrompt = PromptBuilder.BuildSystemPrompt(_settings.RecentDays);
                var userPrompt = PromptBuilder.BuildUserPrompt(query);

                _logger?.LogDebug("Calling Azure OpenAI API (attempt {Attempt}/{MaxRetries})", attempt + 1, maxRetries);

                // Create chat completion options
                var options = new ChatCompletionOptions
                {
                    Temperature = retryTemperature,
                    ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
                        "procurement_query_extraction",
                        BinaryData.FromString(GetJsonSchema()),
                        "Structured extraction of procurement contract query")
                };

                // Call Azure OpenAI
                var messages = new List<ChatMessage>
                {
                    new SystemChatMessage(systemPrompt),
                    new UserChatMessage(userPrompt)
                };

                var response = await chatClient.CompleteChatAsync(messages, options);
                var responseContent = response.Value.Content[0].Text;

                _logger?.LogDebug("Received response from Azure OpenAI");

                // Parse and validate the response
                var extraction = JsonSerializer.Deserialize<Models.ProcurementQueryExtraction>(
                    responseContent,
                    JsonOptions);

                if (extraction == null)
                {
                    throw new ExtractionException("Failed to parse extraction response");
                }

                _logger?.LogInformation("Extraction successful on attempt {Attempt}: {GroupCount} filter group(s)",
                    attempt + 1, extraction.FilterGroups.Count);

                // Convert to dictionary format
                return ExtractionToDict(extraction);
            }
            catch (JsonException ex)
            {
                lastError = ex;
                _logger?.LogWarning("Validation error on attempt {Attempt}, retrying: {Error}", attempt + 1, ex.Message);
                continue;
            }
            catch (RequestFailedException ex)
            {
                lastError = ex;
                _logger?.LogError("Azure OpenAI API error: {Error}", ex.Message);
                throw new AzureOpenAIException(ex.Message, ex);
            }
            catch (Exception ex) when (ex.Message.Contains("extra") || ex.Message.Contains("forbidden"))
            {
                lastError = ex;
                _logger?.LogWarning("Validation error on attempt {Attempt}, retrying: {Error}", attempt + 1, ex.Message);
                continue;
            }
        }

        // All retries failed
        if (lastError != null)
        {
            _logger?.LogError("Extraction failed after {MaxRetries} attempts: {Error}", maxRetries, lastError.Message);
            throw new ExtractionException("Failed to extract query", lastError.Message);
        }

        throw new ExtractionException("Unknown error during extraction");
    }

    /// <summary>
    /// Gets the JSON schema for the extraction response.
    /// </summary>
    private static string GetJsonSchema()
    {
        return """
        {
          "type": "object",
          "properties": {
            "filter_groups": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "StartDate": {
                    "type": ["object", "null"],
                    "properties": {
                      "operator": { "type": "string" },
                      "value": { "type": ["string", "null"] },
                      "start_date": { "type": ["string", "null"] },
                      "end_date": { "type": ["string", "null"] },
                      "recent_days": { "type": ["integer", "null"] }
                    }
                  },
                  "EndDate": {
                    "type": ["object", "null"],
                    "properties": {
                      "operator": { "type": "string" },
                      "value": { "type": ["string", "null"] },
                      "start_date": { "type": ["string", "null"] },
                      "end_date": { "type": ["string", "null"] },
                      "recent_days": { "type": ["integer", "null"] }
                    }
                  },
                  "funded_amount": {
                    "type": ["object", "null"],
                    "properties": {
                      "operator": { "type": "string" },
                      "value": { "type": ["number", "null"] },
                      "min_value": { "type": ["number", "null"] },
                      "max_value": { "type": ["number", "null"] }
                    }
                  },
                  "total_amount": {
                    "type": ["object", "null"],
                    "properties": {
                      "operator": { "type": "string" },
                      "value": { "type": ["number", "null"] },
                      "min_value": { "type": ["number", "null"] },
                      "max_value": { "type": ["number", "null"] }
                    }
                  },
                  "vendor": {
                    "type": ["object", "null"],
                    "properties": {
                      "operator": { "type": "string" },
                      "value": { "type": ["string", "null"] },
                      "values": { "type": ["array", "null"], "items": { "type": "string" } }
                    }
                  },
                  "subdoctype": {
                    "type": ["object", "null"],
                    "properties": {
                      "operator": { "type": "string" },
                      "value": { "type": ["string", "null"] },
                      "values": { "type": ["array", "null"], "items": { "type": "string" } }
                    }
                  },
                  "product_service_code": {
                    "type": ["object", "null"],
                    "properties": {
                      "psc_code": { "type": ["array", "null"], "items": { "type": "string" } },
                      "description": { "type": ["string", "null"] },
                      "level1": {
                        "type": ["object", "null"],
                        "properties": {
                          "code": { "type": "string" },
                          "description": { "type": "string" }
                        }
                      },
                      "level2": {
                        "type": ["object", "null"],
                        "properties": {
                          "code": { "type": "string" },
                          "description": { "type": "string" }
                        }
                      }
                    }
                  },
                  "industry_code": {
                    "type": ["object", "null"],
                    "properties": {
                      "naics_code": { "type": ["array", "null"], "items": { "type": "string" } },
                      "description": { "type": ["string", "null"] },
                      "level1": {
                        "type": ["object", "null"],
                        "properties": {
                          "code": { "type": "string" },
                          "description": { "type": "string" }
                        }
                      },
                      "level2": {
                        "type": ["object", "null"],
                        "properties": {
                          "code": { "type": "string" },
                          "description": { "type": "string" }
                        }
                      }
                    }
                  },
                  "set_aside": {
                    "type": ["object", "null"],
                    "properties": {
                      "description": { "type": ["string", "null"] },
                      "code": { "type": ["array", "null"], "items": { "type": "string" } }
                    }
                  }
                }
              }
            },
            "group_operator_between_groups": { "type": ["string", "null"] },
            "original_query": { "type": "string" }
          },
          "required": ["filter_groups", "original_query"]
        }
        """;
    }

    /// <summary>
    /// Converts a ProcurementQueryExtraction to a dictionary format.
    /// </summary>
    private static Dictionary<string, object?> ExtractionToDict(Models.ProcurementQueryExtraction extraction)
    {
        var filterGroups = new List<Dictionary<string, object?>>();

        foreach (var group in extraction.FilterGroups)
        {
            var groupDict = ConvertFilterGroup(group);
            filterGroups.Add(groupDict);
        }

        return new Dictionary<string, object?>
        {
            ["original_query"] = extraction.OriginalQuery,
            ["filter_groups"] = filterGroups,
            ["group_operator_between_groups"] = extraction.GroupOperatorBetweenGroups
        };
    }

    /// <summary>
    /// Converts a FilterGroup to a dictionary.
    /// </summary>
    private static Dictionary<string, object?> ConvertFilterGroup(FilterGroup group)
    {
        var groupDict = new Dictionary<string, object?>();

        if (group.Subdoctype != null)
        {
            groupDict["subdoctype"] = new Dictionary<string, object?>
            {
                ["operator"] = group.Subdoctype.Operator,
                ["value"] = group.Subdoctype.Value,
                ["values"] = group.Subdoctype.Values
            };
        }

        if (group.StartDate != null)
        {
            groupDict["StartDate"] = new Dictionary<string, object?>
            {
                ["operator"] = group.StartDate.Operator,
                ["value"] = group.StartDate.Value,
                ["start_date"] = group.StartDate.StartDate,
                ["end_date"] = group.StartDate.EndDate,
                ["recent_days"] = group.StartDate.RecentDays
            };
        }

        if (group.EndDate != null)
        {
            groupDict["EndDate"] = new Dictionary<string, object?>
            {
                ["operator"] = group.EndDate.Operator,
                ["value"] = group.EndDate.Value,
                ["start_date"] = group.EndDate.StartDate,
                ["end_date"] = group.EndDate.EndDate,
                ["recent_days"] = group.EndDate.RecentDays
            };
        }

        if (group.TotalAmount != null)
        {
            groupDict["total_amount"] = new Dictionary<string, object?>
            {
                ["operator"] = group.TotalAmount.Operator,
                ["value"] = group.TotalAmount.Value,
                ["min_value"] = group.TotalAmount.MinValue,
                ["max_value"] = group.TotalAmount.MaxValue
            };
        }

        if (group.FundedAmount != null)
        {
            groupDict["funded_amount"] = new Dictionary<string, object?>
            {
                ["operator"] = group.FundedAmount.Operator,
                ["value"] = group.FundedAmount.Value,
                ["min_value"] = group.FundedAmount.MinValue,
                ["max_value"] = group.FundedAmount.MaxValue
            };
        }

        if (group.Vendor != null)
        {
            groupDict["vendor"] = new Dictionary<string, object?>
            {
                ["operator"] = group.Vendor.Operator,
                ["value"] = group.Vendor.Value,
                ["values"] = group.Vendor.Values
            };
        }

        if (group.ProductServiceCode != null)
        {
            groupDict["product_service_code"] = new Dictionary<string, object?>
            {
                ["psc_code"] = group.ProductServiceCode.PscCode,
                ["description"] = group.ProductServiceCode.Description,
                ["level1"] = group.ProductServiceCode.Level1 != null
                    ? new Dictionary<string, object?>
                    {
                        ["code"] = group.ProductServiceCode.Level1.Code,
                        ["description"] = group.ProductServiceCode.Level1.Description
                    }
                    : null,
                ["level2"] = group.ProductServiceCode.Level2 != null
                    ? new Dictionary<string, object?>
                    {
                        ["code"] = group.ProductServiceCode.Level2.Code,
                        ["description"] = group.ProductServiceCode.Level2.Description
                    }
                    : null
            };
        }

        if (group.IndustryCode != null)
        {
            groupDict["industry_code"] = new Dictionary<string, object?>
            {
                ["naics_code"] = group.IndustryCode.NaicsCode,
                ["description"] = group.IndustryCode.Description,
                ["level1"] = group.IndustryCode.Level1 != null
                    ? new Dictionary<string, object?>
                    {
                        ["code"] = group.IndustryCode.Level1.Code,
                        ["description"] = group.IndustryCode.Level1.Description
                    }
                    : null,
                ["level2"] = group.IndustryCode.Level2 != null
                    ? new Dictionary<string, object?>
                    {
                        ["code"] = group.IndustryCode.Level2.Code,
                        ["description"] = group.IndustryCode.Level2.Description
                    }
                    : null
            };
        }

        if (group.SetAside != null)
        {
            groupDict["set_aside"] = new Dictionary<string, object?>
            {
                ["description"] = group.SetAside.Description,
                ["code"] = group.SetAside.Code
            };
        }

        return groupDict;
    }
}

/// <summary>
/// Factory for creating ExtractionService instances.
/// </summary>
public static class ExtractionServiceFactory
{
    private static ExtractionService? _instance;
    private static readonly object _lock = new();

    /// <summary>
    /// Gets a singleton instance of the ExtractionService.
    /// </summary>
    public static ExtractionService GetService(Settings? settings = null)
    {
        if (_instance == null)
        {
            lock (_lock)
            {
                _instance ??= new ExtractionService(settings);
            }
        }
        return _instance;
    }

    /// <summary>
    /// Clears the cached service instance (useful for testing).
    /// </summary>
    public static void ClearCache()
    {
        lock (_lock)
        {
            _instance = null;
        }
    }
}
