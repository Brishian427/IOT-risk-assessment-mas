"""
Show Final Assessment Results
Created: 2025-01-XX
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.main import run_risk_assessment

def show_final_results():
    """Run assessment and display final results"""
    
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
    
    print("=" * 80)
    print("RUNNING RISK ASSESSMENT")
    print("=" * 80)
    print(f"\nScenario:\n{test_scenario}\n")
    print("Processing... (this may take a few minutes)\n")
    
    try:
        result = run_risk_assessment(test_scenario)
        
        print("\n" + "=" * 80)
        print("FINAL SYNTHESIZED ASSESSMENT")
        print("=" * 80)
        
        if result.get("synthesized_draft"):
            draft = result["synthesized_draft"]
            print(f"\n📊 RISK SCORE: {draft.score}/5")
            print(f"\n📝 SUMMARY:")
            print(f"   {draft.reasoning.summary}")
            
            print(f"\n🔑 KEY ARGUMENTS:")
            for i, arg in enumerate(draft.reasoning.key_arguments, 1):
                print(f"   {i}. {arg}")
            
            if draft.reasoning.regulatory_citations:
                print(f"\n📜 REGULATORY CITATIONS:")
                for citation in draft.reasoning.regulatory_citations:
                    print(f"   • {citation}")
            
            if draft.reasoning.vulnerabilities:
                print(f"\n⚠️  VULNERABILITIES:")
                for vuln in draft.reasoning.vulnerabilities:
                    print(f"   • {vuln}")
        else:
            print("\n⚠️  No synthesized draft available")
        
        # Show critiques summary
        critiques = result.get("critiques", [])
        print(f"\n" + "=" * 80)
        print(f"CHALLENGER CRITIQUES ({len(critiques)} total)")
        print("=" * 80)
        
        for critique in critiques:
            status_icon = "✅" if critique.is_valid else "❌"
            print(f"\n{status_icon} {critique.challenger_name.upper().replace('_', ' ')}")
            print(f"   Status: {'VALID' if critique.is_valid else 'INVALID'}")
            print(f"   Confidence: {critique.confidence:.1%}")
            print(f"   Recommendation: {critique.recommendation.upper()}")
            if critique.issues:
                print(f"   Issues Found: {len(critique.issues)}")
                for issue in critique.issues[:3]:  # Show first 3 issues
                    print(f"      • {issue}")
                if len(critique.issues) > 3:
                    print(f"      ... and {len(critique.issues) - 3} more")
        
        # Workflow stats
        print(f"\n" + "=" * 80)
        print("WORKFLOW STATISTICS")
        print("=" * 80)
        print(f"   Total Assessments Generated: {len(result.get('draft_assessments', []))}")
        print(f"   Revision Cycles: {result.get('revision_count', 0)}")
        print(f"   Total Critiques: {len(critiques)}")
        
        print("\n" + "=" * 80)
        print("ASSESSMENT COMPLETE")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    show_final_results()

