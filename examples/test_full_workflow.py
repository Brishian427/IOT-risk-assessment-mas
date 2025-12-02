"""
Full Workflow Test
Created: 2025-01-XX
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import run_risk_assessment


def test_full_workflow():
    """Test the complete workflow end-to-end"""
    
    test_scenario = """
    IoT Smart Door Lock Device:
    - Bluetooth and WiFi connectivity
    - Mobile app control
    - No encryption on Bluetooth communication
    - Firmware updates over unencrypted HTTP
    - Default PIN code (0000)
    - Stores user access logs in plaintext
    - No PSTI Act 2022 compliance documentation
    - Potential CVE-2024-12345 vulnerability (unpatched)
    """
    
    print("=" * 60)
    print("FULL WORKFLOW TEST")
    print("=" * 60)
    print(f"\nTest Scenario:\n{test_scenario}\n")
    
    try:
        result = run_risk_assessment(test_scenario)
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        # Display synthesized draft
        if result.get("synthesized_draft"):
            draft = result["synthesized_draft"]
            print(f"\n[SYNTHESIZED DRAFT]")
            print(f"Model: {draft.model_name}")
            print(f"Risk Score: {draft.score}/5")
            print(f"\nSummary: {draft.reasoning.summary}")
            print(f"\nKey Arguments:")
            for i, arg in enumerate(draft.reasoning.key_arguments, 1):
                print(f"  {i}. {arg}")
            print(f"\nRegulatory Citations:")
            for citation in draft.reasoning.regulatory_citations:
                print(f"  - {citation}")
            print(f"\nVulnerabilities:")
            for vuln in draft.reasoning.vulnerabilities:
                print(f"  - {vuln}")
        
        # Display critiques
        critiques = result.get("critiques", [])
        print(f"\n[CRITIQUES] ({len(critiques)} total)")
        for critique in critiques:
            status = "✓ VALID" if critique.is_valid else "✗ INVALID"
            print(f"\n{critique.challenger_name.upper()}: {status}")
            print(f"  Confidence: {critique.confidence:.2%}")
            print(f"  Recommendation: {critique.recommendation.upper()}")
            if critique.issues:
                print(f"  Issues:")
                for issue in critique.issues:
                    print(f"    - {issue}")
        
        # Display workflow stats
        print(f"\n[WORKFLOW STATS]")
        print(f"  Revision Count: {result.get('revision_count', 0)}")
        print(f"  Total Assessments Generated: {len(result.get('draft_assessments', []))}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_full_workflow()

