"""
Main script to test the procurement query extraction utility.
"""
import json
import sys
import os
from datetime import datetime
from app.services.extraction import get_extraction_service

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


def run_test(queries: list) -> None:
    """
    Run extraction tests on a list of queries.

    Args:
        queries: List of natural language queries to test
    """
    # Create output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("\n" + "="*100)
    print("PROCUREMENT QUERY EXTRACTION UTILITY - TEST RUN")
    print("="*100)

    all_results = []
    success_count = 0
    error_count = 0

    for i, query in enumerate(queries, 1):
        print(f"\n\n{'#'*100}")
        print(f"# TEST CASE {i}")
        print(f"{'#'*100}")

        try:
            service = get_extraction_service()
            result = service.extract(query=query)

            print("\n" + "-"*80)
            print("EXTRACTION OUTPUT:")
            print("-"*80)
            print(json.dumps(result, indent=2))

            all_results.append({
                "test_case": i,
                "query": query,
                "structured_data": result,
                "status": "success"
            })
            success_count += 1

        except Exception as e:
            print(f"\n[ERROR] Error processing query: {e}")
            import traceback
            traceback.print_exc()

            all_results.append({
                "test_case": i,
                "query": query,
                "error": str(e),
                "status": "error"
            })
            error_count += 1

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"test_results_{timestamp}.json")

    output_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(queries),
            "successful": success_count,
            "failed": error_count
        },
        "results": all_results
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print("\n\n" + "="*100)
    print("TEST RUN COMPLETED")
    print("="*100)
    print(f"\nTotal Queries: {len(queries)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {error_count}")
    print(f"\nResults saved to: {output_file}")
    print("="*100 + "\n")


if __name__ == "__main__":
    # Test queries - modify this list to test different queries
    # test_queries = [
    #     "Pull solicitations that reference PSC 7030 or 7050 for software licenses",
    #     "Show me funding opportunities mentioning NAICS 311111 in the last fiscal year",
    #     "Pull solicitations that reference PSC 7030 or 7050 for software licenses",
    #     "awards and solicitations for facilities and building upgrades and maintenance within the last five years",
    # ]

    test_queries = [
        "Show me Army contracts that start before 2024 and end after June 2025"
        # "Show me Army contracts over $10M awarded to Lockheed in FY 2023 OR under $5M awarded to Lockheed in FY 2023",
        # "Contracts over $10M to Lockheed in FY23",
        # "IT services contracts in 2024",
        # "Recent solicitations for cybersecurity",
        # # OR queries (multiple groups)
        # "Contracts over $10M OR under $5M to Lockheed in FY23",
        # "IT services to Boeing OR Lockheed in 2024",
        # "Contracts in Q1 2024 OR Q3 2024",
        # # Complex OR with different service types
        # "IT services over $1M OR construction under $500K in FY24",
        # "Show me IT contracts over $1M in FY 2024",
        # "Pull solicitations that reference PSC 7030 or 7050 for software licenses",
        
        # "Show me recent Army contracts over $10M awarded to Lockheed",
        # "Job Corps center contracts awarded to Historically Underutilized Businesses between 2020 and 2025",
        # "job Corps center contracts over $10M in 2020 or under $5M awarded to Lockheed in FY 2023 awarded to Historically Underutilized Businesses",
        # "job Corps center contracts over $10M in 2020 or over $5M awarded to Lockheed in FY 2023 awarded to Historically Underutilized Businesses",
        # "List aerospace NAICS awards above $5M obligated in FY23",
        # "Contracts awarded for application support, upgrades, or software lifecycle services in 2025",
        # "awards and solicitations for facilities and building upgrades and maintenance within the last five years",
        # "Show me all contract awards for facility maintenance services issued by [Agency Name] in the past two fiscal years, including total obligated amounts and vendors.",
        # "Retrieve assistance awards and grant agreements for small business, innovation or R&D programs funded by [Agency Name] between FY2022 and FY2024, including recipient names and funding amounts",
        # "SOOs for IT Infrastructure ",
        # "Show me awards that have option line items for [specific items or service]",
        # "Construction contracts for new construction or renovations ",
        # "I need a list of all awards that include clause 1234.",
        # "I need a list of all awards that were awarded this Fiscal year.",
        # "Past PWS used for nursing services",
        # "Please list all of the awards which have been made to Microsoft.",
        # "List all solicitation attachments or amendments related to construction or renovation projects under [Agency Name]",
        # "Summarize all awards and modifications issued to [Vendor Name or DUNS] across all [Agency Name] in the last 24 months, and show total obligations by month.",
        # "Acquisition Plans for IT Services over $10 million",
        # "available IT contracts for laptops with x dollar amount remaining",
        # "Contracts with a PoP ending in the next 90 days",
        # "Search for all awards released with total obligation over SAT crated in lat 90 days.",
        # "Please show me a list of all of the current awards related to facilities management.",
        # "Find awards tied to NAICS 541512 for cloud migration support",
        # "Pull solicitations that reference PSC 7030 or 7050 for software licenses",
        # "Show me funding opportunities mentioning NAICS 311111 in the last fiscal year",
        # "List requisitions for PSC for foundry machinery issued in FY24",
    ]

    complex_queries = [
    "Show me construction contracts over $500K in FY 2024",
    "IT services contracts above $2M in 2024",
    "Cybersecurity contracts over $1M in FY 2023",
    "Healthcare contracts above $5M in FY 2024",
    "Software contracts over $1M awarded in 2024",
    "Engineering contracts greater than $10M in FY 2024",
    "Consulting contracts over $500K in fiscal year 2024",
    "Maintenance contracts above $1M in 2024",

    # OR with different amounts + same set-aside
    "8(a) contracts over $10M OR under $1M in FY 2024",
    
    # OR with different set-asides
    # "SDVOSB contracts OR WOSB contracts for IT services in 2024",
    
    # # OR with set-aside + vendor combinations
    # "HUBZone contracts to Lockheed OR small business contracts to Boeing in 2023",
    
    # # Complex: different amounts + vendors + set-aside
    # "SDVOSB contracts over $5M awarded to Raytheon OR WOSB contracts under $2M awarded to General Dynamics in FY 2024",
    
    # # Your original query (should now work correctly)
    # "Job Corps center contracts awarded to Historically Underutilized Businesses between 2020 and 2025",
    
    # # Mixed: set-aside + no set-aside
    # "8(a) contracts over $1M OR delivery orders under $500K to Lockheed in 2024",
    
    # # Triple OR
    # "Small business contracts OR HUBZone solicitations OR SDVOSB awards for cybersecurity services in 2024",
]
    run_test(test_queries)
    #run_test(complex_queries)
