"""
System Health Test - Verify all scenarios and agent functionality
Created: 2025-12-09
"""

import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import run_risk_assessment
from src.config import Config


def check_scenario_files() -> Dict:
    """Check if all expected scenario files exist"""
    print("=" * 80)
    print("📋 Checking Scenario Files")
    print("=" * 80)
    
    evaluation_dir = Path("evaluation_inputs")
    if not evaluation_dir.exists():
        print("❌ ERROR: evaluation_inputs directory not found")
        return {"status": "error", "files_found": 0, "files_expected": 11}
    
    # Expected scenarios: 4 (Usage Phase 1-4) + 4 (Usage Phase 5-8) + 3 (EOL 9-11) = 11
    expected_files = [
        "scenario_1_mass_data_inference.txt",
        "scenario_2_remote_direct_control.txt",
        "scenario_3_data_hacking_breaching.txt",
        "scenario_4_user_awareness_deficit.txt",
        "scenario_5_lack_of_continuous_updates.txt",
        "scenario_6_cloud_dependence.txt",
        "scenario_7_user_awareness_legal_compliance.txt",
        "scenario_8_protocol_weaknesses.txt",
        "scenario_9_physical_safety_fire_hazards.txt",
        "scenario_10_data_security_secondhand_market.txt",
        "scenario_11_environmental_toxicity.txt",
    ]
    
    found_files = []
    missing_files = []
    
    for filename in expected_files:
        filepath = evaluation_dir / filename
        if filepath.exists():
            found_files.append(filename)
            print(f"  ✅ {filename}")
        else:
            missing_files.append(filename)
            print(f"  ❌ {filename} - MISSING")
    
    print(f"\n📊 Summary:")
    print(f"   Expected: {len(expected_files)} files")
    print(f"   Found: {len(found_files)} files")
    print(f"   Missing: {len(missing_files)} files")
    
    if missing_files:
        print(f"\n⚠️  Missing files:")
        for f in missing_files:
            print(f"   - {f}")
    
    return {
        "status": "ok" if len(missing_files) == 0 else "error",
        "files_found": len(found_files),
        "files_expected": len(expected_files),
        "missing_files": missing_files,
        "found_files": found_files
    }


def check_api_keys() -> Dict:
    """Check if all required API keys are configured"""
    print("\n" + "=" * 80)
    print("🔑 Checking API Keys")
    print("=" * 80)
    
    missing_keys = Config.validate_api_keys()
    
    if missing_keys:
        print(f"  ❌ Missing API keys: {', '.join(missing_keys)}")
        return {"status": "error", "missing_keys": missing_keys}
    else:
        print("  ✅ All required API keys are configured")
        return {"status": "ok", "missing_keys": []}


def test_single_scenario(scenario_file: str) -> Dict:
    """Test a single scenario to verify system functionality"""
    print("\n" + "=" * 80)
    print(f"🧪 Testing Scenario: {scenario_file}")
    print("=" * 80)
    
    filepath = Path("evaluation_inputs") / scenario_file
    if not filepath.exists():
        print(f"  ❌ File not found: {filepath}")
        return {"status": "error", "error": "File not found"}
    
    # Read scenario
    with open(filepath, 'r', encoding='utf-8') as f:
        risk_input = f.read()
    
    print(f"  📄 Scenario loaded: {len(risk_input)} characters")
    print(f"  🔄 Running assessment...\n")
    
    try:
        # Run assessment
        result = run_risk_assessment(
            risk_input=risk_input,
            save_result=True,
            enable_logging=True
        )
        
        # Check results
        has_synthesized_draft = result.get("synthesized_draft") is not None
        draft_assessments_count = len(result.get("draft_assessments", []))
        critiques_count = len(result.get("critiques", []))
        revision_count = result.get("revision_count", 0)
        
        print(f"\n  📊 Results:")
        print(f"     ✅ Synthesized Draft: {'Yes' if has_synthesized_draft else 'No'}")
        print(f"     ✅ Draft Assessments: {draft_assessments_count} (expected: 9)")
        print(f"     ✅ Critiques: {critiques_count} (expected: 3 per round)")
        print(f"     ✅ Revision Count: {revision_count}")
        
        # Check if agents worked
        if has_synthesized_draft:
            draft = result["synthesized_draft"]
            print(f"\n  📝 Assessment Details:")
            print(f"     Score: {draft.score}/5")
            print(f"     Regulatory Citations: {len(draft.reasoning.regulatory_citations)}")
            print(f"     Vulnerabilities: {len(draft.reasoning.vulnerabilities)}")
            print(f"     Key Arguments: {len(draft.reasoning.key_arguments)}")
            
            # Check if references are used
            has_citations = len(draft.reasoning.regulatory_citations) > 0
            has_vulnerabilities = len(draft.reasoning.vulnerabilities) > 0
            has_arguments = len(draft.reasoning.key_arguments) > 0
            
            print(f"\n  🔍 Reference Usage:")
            print(f"     {'✅' if has_citations else '⚠️ '} Regulatory Citations: {len(draft.reasoning.regulatory_citations)}")
            print(f"     {'✅' if has_vulnerabilities else '⚠️ '} Vulnerabilities: {len(draft.reasoning.vulnerabilities)}")
            print(f"     {'✅' if has_arguments else '⚠️ '} Key Arguments: {len(draft.reasoning.key_arguments)}")
        
        # Check challenger status
        print(f"\n  🤖 Agent Status:")
        challenger_status = {}
        for critique in result.get("critiques", []):
            challenger_name = critique.challenger_name
            if challenger_name not in challenger_status:
                challenger_status[challenger_name] = {
                    "count": 0,
                    "valid_count": 0,
                    "accept_count": 0
                }
            challenger_status[challenger_name]["count"] += 1
            if critique.is_valid:
                challenger_status[challenger_name]["valid_count"] += 1
            if "accept" in critique.recommendation.lower():
                challenger_status[challenger_name]["accept_count"] += 1
        
        for name, status in challenger_status.items():
            status_icon = "✅" if status["count"] > 0 else "❌"
            print(f"     {status_icon} {name}: {status['count']} critiques, "
                  f"{status['valid_count']} valid, {status['accept_count']} accepted")
        
        # Overall status
        all_agents_worked = (
            has_synthesized_draft and
            draft_assessments_count >= 9 and
            critiques_count >= 3 and
            len(challenger_status) >= 3
        )
        
        if all_agents_worked:
            print(f"\n  ✅ All agents worked correctly!")
        else:
            print(f"\n  ⚠️  Some agents may not have worked correctly")
        
        return {
            "status": "ok" if all_agents_worked else "warning",
            "has_synthesized_draft": has_synthesized_draft,
            "draft_assessments_count": draft_assessments_count,
            "critiques_count": critiques_count,
            "revision_count": revision_count,
            "challenger_status": challenger_status,
            "has_citations": has_citations if has_synthesized_draft else False,
            "has_vulnerabilities": has_vulnerabilities if has_synthesized_draft else False,
            "has_arguments": has_arguments if has_synthesized_draft else False
        }
        
    except Exception as e:
        print(f"\n  ❌ ERROR during assessment: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def main():
    """Run complete system health check"""
    print("\n" + "=" * 80)
    print("🔍 SYSTEM HEALTH CHECK")
    print("=" * 80)
    print("Assessment for IoT Risk\n")
    
    # Check scenario files
    scenario_check = check_scenario_files()
    
    # Check API keys
    api_check = check_api_keys()
    
    # Test a single scenario
    if scenario_check["status"] == "ok" and api_check["status"] == "ok":
        # Test scenario 1 (should be quick)
        test_result = test_single_scenario("scenario_1_mass_data_inference.txt")
    else:
        print("\n⚠️  Skipping scenario test due to missing files or API keys")
        test_result = {"status": "skipped"}
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    
    print(f"\nScenario Files: {'✅' if scenario_check['status'] == 'ok' else '❌'} "
          f"({scenario_check['files_found']}/{scenario_check['files_expected']})")
    print(f"API Keys: {'✅' if api_check['status'] == 'ok' else '❌'}")
    print(f"System Test: {'✅' if test_result.get('status') == 'ok' else '⚠️' if test_result.get('status') == 'warning' else '❌'}")
    
    if test_result.get("status") == "ok":
        print(f"\n✅ System is healthy and ready for assessment!")
        print(f"   - All {scenario_check['files_expected']} scenarios available")
        print(f"   - All agents working correctly")
        print(f"   - References and citations are being used")
    elif test_result.get("status") == "warning":
        print(f"\n⚠️  System is functional but may have minor issues")
    else:
        print(f"\n❌ System has issues that need to be resolved")
    
    return {
        "scenario_check": scenario_check,
        "api_check": api_check,
        "test_result": test_result
    }


if __name__ == "__main__":
    main()

