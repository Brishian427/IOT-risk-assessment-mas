"""
Analyze Challenger Pass Rates Across All Evaluation Results
Created: 2025-12-09
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def analyze_challenger_performance(results_dir: str = "results") -> Dict:
    """Analyze challenger pass rates from all assessment results"""
    
    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"Error: Results directory '{results_dir}' not found.")
        return {}
    
    # Get all assessment JSON files
    result_files = sorted(list(results_path.glob("assessment_*.json")))
    
    if not result_files:
        print(f"No assessment files found in '{results_dir}'.")
        return {}
    
    print(f"📊 Analyzing {len(result_files)} assessment results...\n")
    
    # Statistics
    total_assessments = 0
    assessments_with_3_revisions = 0
    assessments_reaching_2_3_majority = 0
    assessments_not_reaching_2_3_majority = 0
    
    # Detailed breakdown
    detailed_results = []
    
    for file_path in result_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract metadata - revision_count can be in metadata or output
            risk_input = data.get("input", {}).get("risk_input", "") or data.get("input", {}).get("risk_scenario", "")
            revision_count = data.get("metadata", {}).get("revision_count", 0) or data.get("output", {}).get("revision_count", 0)
            critiques = data.get("output", {}).get("critiques", [])
            
            total_assessments += 1
            
            # Only analyze assessments that reached 3 revisions
            if revision_count >= 3:
                assessments_with_3_revisions += 1
                
                # Get critiques from the final round (last 3 critiques, one from each challenger)
                final_critiques = critiques[-3:] if len(critiques) >= 3 else critiques
                
                # Count pass rate
                passed_count = 0
                challenger_details = []
                
                for critique in final_critiques:
                    challenger_name = critique.get("challenger_name", "unknown")
                    is_valid = critique.get("is_valid", False)
                    recommendation = critique.get("recommendation", "").lower()
                    
                    # Pass criteria: is_valid=True AND recommendation contains "accept"
                    passed = is_valid and "accept" in recommendation
                    if passed:
                        passed_count += 1
                    
                    challenger_details.append({
                        "name": challenger_name,
                        "is_valid": is_valid,
                        "recommendation": critique.get("recommendation", ""),
                        "passed": passed
                    })
                
                total_challengers = len(final_critiques)
                pass_rate = passed_count / total_challengers if total_challengers > 0 else 0
                reached_2_3 = pass_rate >= (2/3)
                
                if reached_2_3:
                    assessments_reaching_2_3_majority += 1
                else:
                    assessments_not_reaching_2_3_majority += 1
                
                # Extract scenario name from risk input (first line usually)
                scenario_name = risk_input.split('\n')[0] if risk_input else "Unknown"
                if "Lifecycle Stage:" in scenario_name:
                    scenario_name = risk_input.split('\n')[1] if len(risk_input.split('\n')) > 1 else "Unknown"
                
                detailed_results.append({
                    "file": file_path.name,
                    "scenario": scenario_name[:60],  # Truncate for display
                    "revision_count": revision_count,
                    "total_challengers": total_challengers,
                    "passed_count": passed_count,
                    "pass_rate": pass_rate,
                    "reached_2_3": reached_2_3,
                    "challenger_details": challenger_details
                })
        
        except Exception as e:
            print(f"⚠️  Error processing {file_path.name}: {e}")
            continue
    
    # Print summary
    print("=" * 80)
    print("📈 CHALLENGER PASS RATE ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Assessments: {total_assessments}")
    print(f"Assessments with 3+ Revisions: {assessments_with_3_revisions}")
    print(f"\n✅ Reached 2/3 Majority: {assessments_reaching_2_3_majority}")
    print(f"❌ Did NOT Reach 2/3 Majority: {assessments_not_reaching_2_3_majority}")
    
    if assessments_with_3_revisions > 0:
        success_rate = (assessments_reaching_2_3_majority / assessments_with_3_revisions) * 100
        print(f"\n📊 Success Rate (2/3 majority): {success_rate:.1f}%")
    
    # Print detailed results for cases that did NOT reach 2/3 majority
    if assessments_not_reaching_2_3_majority > 0:
        print("\n" + "=" * 80)
        print("❌ ASSESSMENTS THAT DID NOT REACH 2/3 MAJORITY")
        print("=" * 80)
        
        for result in detailed_results:
            if not result["reached_2_3"]:
                print(f"\n📄 File: {result['file']}")
                print(f"   Scenario: {result['scenario']}")
                print(f"   Revision Count: {result['revision_count']}")
                print(f"   Pass Rate: {result['passed_count']}/{result['total_challengers']} ({result['pass_rate']*100:.1f}%)")
                print(f"   Challenger Details:")
                for ch in result['challenger_details']:
                    status = "✅ PASS" if ch['passed'] else "❌ FAIL"
                    print(f"     - {ch['name']}: {status} (is_valid={ch['is_valid']}, recommendation='{ch['recommendation']}')")
    
    # Print all results summary table
    print("\n" + "=" * 80)
    print("📋 ALL ASSESSMENTS SUMMARY (3+ Revisions)")
    print("=" * 80)
    print(f"{'File':<30} {'Scenario':<30} {'Pass Rate':<12} {'2/3?':<6}")
    print("-" * 80)
    
    for result in detailed_results:
        scenario_short = result['scenario'][:28]
        pass_rate_str = f"{result['passed_count']}/{result['total_challengers']} ({result['pass_rate']*100:.0f}%)"
        reached_str = "✅ YES" if result['reached_2_3'] else "❌ NO"
        print(f"{result['file']:<30} {scenario_short:<30} {pass_rate_str:<12} {reached_str:<6}")
    
    return {
        "total_assessments": total_assessments,
        "assessments_with_3_revisions": assessments_with_3_revisions,
        "reached_2_3_majority": assessments_reaching_2_3_majority,
        "not_reaching_2_3_majority": assessments_not_reaching_2_3_majority,
        "detailed_results": detailed_results
    }


if __name__ == "__main__":
    analyze_challenger_performance()

