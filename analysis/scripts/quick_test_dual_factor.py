"""
Quick Test for Dual-Factor Risk Assessment System
Created: 2025-12-09
Tests if the system works correctly with new dual-factor assessment format
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import run_risk_assessment

# Simple test scenario
test_input = """Lifecycle Stage: Usage Phase
Risk Category: Mass Data Inference

Scenario Description:
Smart appliances continuously collect and transmit granular behavioral data as part of their core functionality.

Risk Mechanism:
Metadata Analysis: Even without 'hacking', legitimate data streams can be analyzed to infer intimate household details.

Context Data:
- GCHQ intervened in the UK smart meter rollout due to fears that usage data could reveal unoccupied homes
- Data collection happens by default as part of standard device operation

Task:
Evaluate the Risk Score (Frequency x Impact). For 'Frequency/Likelihood', ask yourself: 'Is this risk state a constant feature of the device, a widespread vulnerability, or a rare targeted attack?' This data collection happens by default (systemic frequency = 5). Assess the severity of privacy erosion and physical security compromise (burglary).
"""

print("=" * 80)
print("🧪 QUICK TEST: Dual-Factor Risk Assessment System")
print("=" * 80)
print("\n📋 Test Scenario: Mass Data Inference")
print(f"Input Length: {len(test_input)} characters\n")

try:
    print("🔄 Running assessment...\n")
    result = run_risk_assessment(
        risk_input=test_input,
        save_result=True,
        enable_logging=True
    )
    
    print("\n" + "=" * 80)
    print("✅ TEST RESULTS")
    print("=" * 80)
    
    # Check if synthesized_draft exists
    if not result.get("synthesized_draft"):
        print("❌ ERROR: No synthesized_draft generated!")
        sys.exit(1)
    
    draft = result["synthesized_draft"]
    
    # Check legacy score
    print(f"\n📊 Legacy Score: {draft.score}/5")
    
    # Check dual-factor assessment
    if draft.risk_assessment:
        ra = draft.risk_assessment
        print(f"\n✅ Dual-Factor Assessment Found:")
        print(f"   Frequency Score: {ra.frequency_score}/5")
        print(f"   Frequency Rationale: {ra.frequency_rationale[:100]}...")
        print(f"   Impact Score: {ra.impact_score}/5")
        print(f"   Impact Rationale: {ra.impact_rationale[:100]}...")
        print(f"   Final Risk Score: {ra.final_risk_score}/25")
        print(f"   Risk Classification: {ra.risk_classification}")
        
        # Verify calculation
        expected = ra.frequency_score * ra.impact_score
        if ra.final_risk_score == expected:
            print(f"   ✅ Calculation Correct: {ra.frequency_score} × {ra.impact_score} = {ra.final_risk_score}")
        else:
            print(f"   ⚠️  Calculation Mismatch: Expected {expected}, Got {ra.final_risk_score}")
        
        # Check classification
        score = ra.final_risk_score
        if score >= 20:
            expected_class = "Critical"
        elif score >= 12:
            expected_class = "High"
        elif score >= 6:
            expected_class = "Medium"
        else:
            expected_class = "Low"
        
        if ra.risk_classification == expected_class:
            print(f"   ✅ Classification Correct: {ra.risk_classification}")
        else:
            print(f"   ⚠️  Classification Mismatch: Expected {expected_class}, Got {ra.risk_classification}")
    else:
        print("\n❌ ERROR: No risk_assessment breakdown found!")
        print("   The dual-factor assessment is missing!")
        sys.exit(1)
    
    # Check reasoning
    print(f"\n📝 Reasoning:")
    print(f"   Summary: {draft.reasoning.summary[:100]}...")
    print(f"   Key Arguments: {len(draft.reasoning.key_arguments)}")
    print(f"   Regulatory Citations: {len(draft.reasoning.regulatory_citations)}")
    print(f"   Vulnerabilities: {len(draft.reasoning.vulnerabilities)}")
    
    # Check critiques
    critiques = result.get("critiques", [])
    print(f"\n🤖 Challengers:")
    print(f"   Total Critiques: {len(critiques)}")
    
    challenger_names = set()
    for critique in critiques:
        challenger_names.add(critique.challenger_name)
        if critique.challenger_name == "challenger_a":
            print(f"   ✅ Challenger A: {len([c for c in critiques if c.challenger_name == 'challenger_a'])} critiques")
        elif critique.challenger_name == "challenger_b":
            print(f"   ✅ Challenger B: {len([c for c in critiques if c.challenger_name == 'challenger_b'])} critiques")
        elif critique.challenger_name == "challenger_c":
            print(f"   ✅ Challenger C: {len([c for c in critiques if c.challenger_name == 'challenger_c'])} critiques")
    
    if len(challenger_names) >= 3:
        print(f"   ✅ All 3 challengers worked")
    else:
        print(f"   ⚠️  Only {len(challenger_names)} challengers found")
    
    # Check revision count
    revision_count = result.get("revision_count", 0)
    print(f"\n🔄 Workflow:")
    print(f"   Revision Count: {revision_count}")
    print(f"   Total Cycles: {revision_count + 1}")
    
    # Final validation
    print(f"\n" + "=" * 80)
    print("📋 CONTENT CHECKLIST")
    print("=" * 80)
    
    checks = {
        "Legacy Score (1-5)": draft.score is not None and 1 <= draft.score <= 5,
        "Dual-Factor Assessment": draft.risk_assessment is not None,
        "Frequency Score": draft.risk_assessment.frequency_score if draft.risk_assessment else False,
        "Frequency Rationale": bool(draft.risk_assessment.frequency_rationale) if draft.risk_assessment else False,
        "Impact Score": draft.risk_assessment.impact_score if draft.risk_assessment else False,
        "Impact Rationale": bool(draft.risk_assessment.impact_rationale) if draft.risk_assessment else False,
        "Final Risk Score (1-25)": draft.risk_assessment.final_risk_score if draft.risk_assessment else False,
        "Risk Classification": bool(draft.risk_assessment.risk_classification) if draft.risk_assessment else False,
        "Calculation Correct": draft.risk_assessment.final_risk_score == draft.risk_assessment.frequency_score * draft.risk_assessment.impact_score if draft.risk_assessment else False,
        "Summary": bool(draft.reasoning.summary),
        "Key Arguments": len(draft.reasoning.key_arguments) > 0,
        "Regulatory Citations": len(draft.reasoning.regulatory_citations) >= 0,  # Can be 0
        "Vulnerabilities": len(draft.reasoning.vulnerabilities) >= 0,  # Can be 0
        "Challenger A Worked": any(c.challenger_name == "challenger_a" for c in critiques),
        "Challenger B Worked": any(c.challenger_name == "challenger_b" for c in critiques),
        "Challenger C Worked": any(c.challenger_name == "challenger_c" for c in critiques),
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False
    
    print(f"\n" + "=" * 80)
    if all_passed:
        print("✅ ALL CHECKS PASSED - System is working correctly!")
    else:
        print("⚠️  SOME CHECKS FAILED - Review the issues above")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR during test: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

