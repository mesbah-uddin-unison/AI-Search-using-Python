using System.Text.Json;
using Microsoft.Extensions.Configuration;
using ProcurementQueryExtraction.Core.Configuration;
using ProcurementQueryExtraction.Core.Services;

namespace ProcurementQueryExtraction.Console;

class Program
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        WriteIndented = true,
        DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
    };

    static async Task Main(string[] args)
    {
        System.Console.OutputEncoding = System.Text.Encoding.UTF8;

        // Build configuration from environment variables and appsettings.json
        var configuration = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json", optional: true)
            .AddEnvironmentVariables()
            .Build();

        try
        {
            // Get settings
            var settings = SettingsProvider.GetSettings(configuration);
            System.Console.WriteLine($"Connected to Azure OpenAI endpoint: {settings.AzureOpenAIEndpoint}");
            System.Console.WriteLine($"Deployment: {settings.AzureOpenAIDeployment}");
            System.Console.WriteLine();

            // Run tests
            await RunTests(settings);
        }
        catch (InvalidOperationException ex)
        {
            System.Console.WriteLine($"Configuration Error: {ex.Message}");
            System.Console.WriteLine();
            System.Console.WriteLine("Please ensure the following environment variables are set:");
            System.Console.WriteLine("  - AZURE_OPENAI_ENDPOINT");
            System.Console.WriteLine("  - AZURE_OPENAI_API_KEY");
            System.Console.WriteLine("  - AZURE_OPENAI_DEPLOYMENT");
            Environment.Exit(1);
        }
        catch (Exception ex)
        {
            System.Console.WriteLine($"Error: {ex.Message}");
            Environment.Exit(1);
        }
    }

    static async Task RunTests(Settings settings)
    {
        var testQueries = new List<string>
        {
            "Show me construction contracts over $500K in FY 2024",
            "IT services contracts above $2M in 2024",
            "Cybersecurity contracts over $1M in FY 2023",
            "Healthcare contracts above $5M in FY 2024",
            "Software contracts over $1M awarded in 2024",
            "Engineering contracts greater than $10M in FY 2024",
            "Consulting contracts over $500K in fiscal year 2024",
            "Maintenance contracts above $1M in 2024",
            "8(a) contracts over $10M OR under $1M in FY 2024"
        };

        var service = new ExtractionService(settings);
        var allResults = new List<object>();
        int successCount = 0;
        int errorCount = 0;

        for (int i = 0; i < testQueries.Count; i++)
        {
            var query = testQueries[i];
            System.Console.WriteLine();
            System.Console.WriteLine(new string('#', 100));
            System.Console.WriteLine($"# TEST CASE {i + 1}");
            System.Console.WriteLine(new string('#', 100));
            System.Console.WriteLine($"Query: {query}");

            try
            {
                var result = await service.ExtractAsync(query);

                System.Console.WriteLine();
                System.Console.WriteLine(new string('-', 80));
                System.Console.WriteLine("EXTRACTION OUTPUT:");
                System.Console.WriteLine(new string('-', 80));
                System.Console.WriteLine(JsonSerializer.Serialize(result, JsonOptions));

                allResults.Add(new
                {
                    test_case = i + 1,
                    query = query,
                    structured_data = result,
                    status = "success"
                });
                successCount++;
            }
            catch (Exception ex)
            {
                System.Console.WriteLine();
                System.Console.WriteLine($"[ERROR] Error processing query: {ex.Message}");

                allResults.Add(new
                {
                    test_case = i + 1,
                    query = query,
                    error = ex.Message,
                    status = "error"
                });
                errorCount++;
            }
        }

        // Summary
        System.Console.WriteLine();
        System.Console.WriteLine(new string('=', 100));
        System.Console.WriteLine("TEST SUMMARY");
        System.Console.WriteLine(new string('=', 100));
        System.Console.WriteLine($"Total: {testQueries.Count}");
        System.Console.WriteLine($"Success: {successCount}");
        System.Console.WriteLine($"Errors: {errorCount}");

        // Save results
        var outputDir = Path.Combine(Directory.GetCurrentDirectory(), "output");
        Directory.CreateDirectory(outputDir);

        var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
        var outputFile = Path.Combine(outputDir, $"test_results_{timestamp}.json");

        var finalOutput = new
        {
            generated_at = DateTime.Now.ToString("o"),
            total_queries = testQueries.Count,
            successful = successCount,
            errors = errorCount,
            results = allResults
        };

        await File.WriteAllTextAsync(outputFile, JsonSerializer.Serialize(finalOutput, JsonOptions));
        System.Console.WriteLine();
        System.Console.WriteLine($"Results saved to: {outputFile}");
    }
}
