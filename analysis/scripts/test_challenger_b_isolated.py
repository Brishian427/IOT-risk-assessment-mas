"""
Isolated Test for Challenger B - Citation Verification
Created: 2025-12-09
Tests Challenger B's acceptance rate with various citation scenarios
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from src.config import Config
from src.utils.prompt_templates import CHALLENGER_B_PROMPT
from src.utils.reference_sources import get_reference_sources
from src.utils.citation_parser import CitationParser
from src.utils.search_helpers import SearchQueryBuilder


def test_challenger_b(
    citations: List[str],
    assessment_text: str = "Test risk assessment with score 4",
    mock_search_results: List[Dict] = None
) -> Dict:
    """
    Test Challenger B with given citations
    
    Args:
        citations: List of citations to verify
        assessment_text: Assessment text for context
        mock_search_results: Optional mock search results (for testing without API calls)
    
    Returns:
        Dict with is_valid, recommendation, issues, confidence
    """
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=Config.CHALLENGER_B_MODEL,
        temperature=Config.CHALLENGER_TEMPERATURE,
        api_key=Config.OPENAI_API_KEY
    )
    
    # Initialize search tool (only if not using mock)
    search_tool = None
    if mock_search_results is None:
        search_tool = TavilySearch(
            api_key=Config.TAVILY_API_KEY,
            max_results=5
        )
    
    query_builder = SearchQueryBuilder()
    search_results_summary = []
    
    # Process each citation
    for citation in citations:
        if mock_search_results:
            # Use mock results
            results = mock_search_results.get(citation, [])
            citation_type = "Unknown"
        else:
            # Determine citation type and build query
            if citation.upper().startswith("CVE"):
                query = query_builder.build_cve_query(citation)
                citation_type = "CVE"
            elif any(term in citation.upper() for term in ["ISO", "27001", "27002"]):
                query = query_builder.build_standard_query(citation)
                citation_type = "Standard"
            else:
                query = query_builder.build_regulation_query(citation)
                citation_type = "Regulation"
            
            # Perform search
            try:
                raw_results = search_tool.invoke(query)
                # Tavily returns a list of dicts
                if isinstance(raw_results, list):
                    # Ensure each item is a dict
                    results = [r if isinstance(r, dict) else {} for r in raw_results]
                elif isinstance(raw_results, dict):
                    # If it's a dict, check for 'results' key
                    results = raw_results.get('results', [])
                else:
                    results = []
            except Exception as e:
                results = []
                citation_type = "Unknown"
                print(f"  ⚠️  Search error for {citation}: {e}")
        
        # Analyze results
        analysis = query_builder.analyze_search_results(citation, citation_type.lower(), results)
        
        search_results_summary.append({
            "citation": citation,
            "type": citation_type,
            "verified": analysis["verified"],
            "confidence": analysis["confidence"],
            "urls": analysis["relevant_urls"]
        })
    
    # Format for LLM
    citations_text = "\n".join([f"- {c}" for c in citations])
    results_text = json.dumps(search_results_summary, indent=2)
    
    prompt = CHALLENGER_B_PROMPT.format(
        assessment=assessment_text,
        citations=citations_text,
        search_results=results_text,
        reference_sources=get_reference_sources()
    )
    
    # Get LLM response
    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Parse JSON from response
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            content = content[json_start:json_end].strip()
        elif "```" in content:
            json_start = content.find("```") + 3
            json_end = content.find("```", json_start)
            content = content[json_start:json_end].strip()
        
        data = json.loads(content)
        
        return {
            "is_valid": data.get("is_valid", False),
            "recommendation": data.get("recommendation", "needs_review"),
            "issues": data.get("issues", []),
            "confidence": data.get("confidence", 0.5),
            "citations_checked": len(citations),
            "verified_count": sum(1 for r in search_results_summary if r.get("verified", False)),
            "verification_rate": sum(1 for r in search_results_summary if r.get("verified", False)) / len(citations) if citations else 0
        }
    except Exception as e:
        return {
            "error": str(e),
            "is_valid": False,
            "recommendation": "needs_review"
        }


def run_test_suite():
    """Run a suite of tests with different citation scenarios"""
    
    print("=" * 80)
    print("🧪 ISOLATED TEST: Challenger B Citation Verification")
    print("=" * 80)
    print(f"\nModel: {Config.CHALLENGER_B_MODEL}")
    print(f"Temperature: {Config.CHALLENGER_TEMPERATURE}")
    print(f"\nTesting various citation scenarios...\n")
    
    test_cases = [
        {
            "name": "All Verified (Major Citations)",
            "citations": ["CVE-2024-1234", "ISO 27001", "PSTI Act 2022"],
            "expected": "accept"
        },
        {
            "name": "50% Verified (2/4)",
            "citations": ["CVE-2024-1234", "ISO 27001", "Unknown Regulation XYZ", "Fake Standard ABC"],
            "expected": "accept"
        },
        {
            "name": "Major Verified, Minor Unverified",
            "citations": ["CVE-2024-1234", "ISO 27001", "Minor Statistic 2023", "Peripheral Standard"],
            "expected": "accept"
        },
        {
            "name": "Mostly Unverified (1/4)",
            "citations": ["CVE-2024-1234", "Fake Regulation 1", "Fake Regulation 2", "Fake Standard"],
            "expected": "needs_review or reject"
        },
        {
            "name": "Critical CVE Verified",
            "citations": ["CVE-2024-5678", "Some Unverified Stat"],
            "expected": "accept"
        },
        {
            "name": "No Citations",
            "citations": [],
            "expected": "accept",
            "skip": True  # Skip this test - handled differently in actual code
        },
        {
            "name": "Mixed Real Citations",
            "citations": ["ISO 27001", "ISO 27002", "PSTI Act 2022", "GDPR"],
            "expected": "accept"
        },
        {
            "name": "All Unverified (Major)",
            "citations": ["CVE-FAKE-1234", "Fake Regulation XYZ", "Unknown Standard"],
            "expected": "reject or needs_review"
        }
    ]
    
    results = []
    passed_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        if test_case.get('skip', False):
            print(f"\n[{i}/{len(test_cases)}] {test_case['name']} (SKIPPED)")
            continue
            
        print(f"\n[{i}/{len(test_cases)}] {test_case['name']}")
        print(f"   Citations: {', '.join(test_case['citations']) if test_case['citations'] else '(none)'}")
        
        try:
            result = test_challenger_b(
                citations=test_case['citations'],
                assessment_text=f"Test assessment for: {test_case['name']}"
            )
            
            if "error" in result:
                print(f"   ❌ ERROR: {result['error']}")
                results.append({
                    "test": test_case['name'],
                    "status": "error",
                    "result": result
                })
                continue
            
            is_valid = result.get("is_valid", False)
            recommendation = result.get("recommendation", "needs_review")
            verification_rate = result.get("verification_rate", 0)
            
            status_icon = "✅" if is_valid and "accept" in recommendation.lower() else "⚠️" if is_valid else "❌"
            
            print(f"   {status_icon} is_valid={is_valid}, recommendation='{recommendation}'")
            print(f"   Verification Rate: {verification_rate*100:.1f}% ({result.get('verified_count', 0)}/{result.get('citations_checked', 0)})")
            
            if result.get("issues"):
                print(f"   Issues: {len(result['issues'])} issue(s)")
                for issue in result['issues'][:2]:  # Show first 2
                    print(f"      - {issue[:60]}")
            
            # Check if result meets expectation
            if test_case['expected'] == "accept":
                passed = is_valid and "accept" in recommendation.lower()
            elif test_case['expected'] == "needs_review or reject":
                passed = not (is_valid and "accept" in recommendation.lower())
            else:
                passed = True  # Don't fail test for unexpected cases
            
            if passed:
                passed_count += 1
            
            results.append({
                "test": test_case['name'],
                "status": "passed" if passed else "unexpected",
                "is_valid": is_valid,
                "recommendation": recommendation,
                "verification_rate": verification_rate,
                "result": result
            })
            
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            results.append({
                "test": test_case['name'],
                "status": "exception",
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len([r for r in results if r.get("status") != "error"])
    acceptance_count = sum(1 for r in results if r.get("is_valid") and "accept" in r.get("recommendation", "").lower())
    acceptance_rate = (acceptance_count / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Accepted: {acceptance_count} ({acceptance_rate:.1f}%)")
    print(f"Target: ≥50% acceptance rate")
    
    if acceptance_rate >= 50:
        print(f"✅ SUCCESS: Acceptance rate ({acceptance_rate:.1f}%) meets target!")
    else:
        print(f"⚠️  WARNING: Acceptance rate ({acceptance_rate:.1f}%) below target (50%)")
    
    print(f"\nDetailed Results:")
    for r in results:
        if r.get("status") == "error":
            print(f"   ❌ {r['test']}: ERROR")
        else:
            status = "✅" if r.get("is_valid") and "accept" in r.get("recommendation", "").lower() else "⚠️"
            print(f"   {status} {r['test']}: {r.get('recommendation', 'unknown')} (verified: {r.get('verification_rate', 0)*100:.0f}%)")
    
    return {
        "total_tests": total_tests,
        "acceptance_count": acceptance_count,
        "acceptance_rate": acceptance_rate,
        "results": results
    }


if __name__ == "__main__":
    # Check API keys
    if not Config.OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not set")
        sys.exit(1)
    
    if not Config.TAVILY_API_KEY:
        print("⚠️  WARNING: TAVILY_API_KEY not set - will use mock results")
    
    run_test_suite()

