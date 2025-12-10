"""
Analyze Challenger Agreement Patterns
Created: 2025-12-09
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

def analyze_challenger_agreement(results_dir: str = "results") -> Dict:
    """Analyze how often challengers agree with each other"""
    
    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"Error: Results directory '{results_dir}' not found.")
        return {}
    
    result_files = sorted(list(results_path.glob("assessment_*.json")))
    
    if not result_files:
        print(f"No assessment files found in '{results_dir}'.")
        return {}
    
    print(f"📊 Analyzing Challenger Agreement in {len(result_files)} assessments...\n")
    
    # Statistics
    total_rounds = 0
    rounds_with_agreement = 0
    rounds_with_full_agreement = 0
    rounds_with_2_3_agreement = 0
    rounds_with_no_agreement = 0
    
    # Per-challenger statistics
    challenger_pass_rates = defaultdict(int)
    challenger_total_rounds = defaultdict(int)
    
    # Agreement patterns
    agreement_patterns = Counter()  # e.g., "A+B+C", "A+B", "A only", "none"
    
    # Detailed breakdown
    detailed_rounds = []
    
    for file_path in result_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            critiques = data.get("output", {}).get("critiques", [])
            revision_count = data.get("metadata", {}).get("revision_count", 0) or data.get("output", {}).get("revision_count", 0)
            
            # Analyze each round (every 3 critiques = 1 round)
            for round_num in range(revision_count + 1):  # 0 to revision_count (inclusive)
                round_critiques = critiques[round_num * 3:(round_num + 1) * 3]
                
                if len(round_critiques) < 3:
                    continue
                
                total_rounds += 1
                
                # Analyze each challenger
                challenger_status = {}
                passed_challengers = []
                
                for critique in round_critiques:
                    challenger_name = critique.get("challenger_name", "unknown")
                    is_valid = critique.get("is_valid", False)
                    recommendation = critique.get("recommendation", "").lower()
                    
                    passed = is_valid and "accept" in recommendation
                    challenger_status[challenger_name] = {
                        "passed": passed,
                        "is_valid": is_valid,
                        "recommendation": critique.get("recommendation", "")
                    }
                    
                    challenger_total_rounds[challenger_name] += 1
                    if passed:
                        challenger_pass_rates[challenger_name] += 1
                        passed_challengers.append(challenger_name)
                
                # Determine agreement pattern
                passed_count = len(passed_challengers)
                
                if passed_count == 3:
                    pattern = "All 3 (A+B+C)"
                    rounds_with_full_agreement += 1
                    rounds_with_agreement += 1
                    rounds_with_2_3_agreement += 1
                elif passed_count == 2:
                    pattern = f"2/3 ({'+'.join(passed_challengers)})"
                    rounds_with_agreement += 1
                    rounds_with_2_3_agreement += 1
                elif passed_count == 1:
                    pattern = f"1/3 ({passed_challengers[0]} only)"
                    rounds_with_agreement += 1
                else:
                    pattern = "None (0/3)"
                    rounds_with_no_agreement += 1
                
                agreement_patterns[pattern] += 1
                
                detailed_rounds.append({
                    "file": file_path.name,
                    "round": round_num,
                    "pattern": pattern,
                    "passed_count": passed_count,
                    "challenger_status": challenger_status
                })
        
        except Exception as e:
            print(f"⚠️  Error processing {file_path.name}: {e}")
            continue
    
    # Print summary
    print("=" * 80)
    print("🤝 CHALLENGER AGREEMENT ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Rounds Analyzed: {total_rounds}")
    print(f"\n📊 Agreement Statistics:")
    print(f"   Full Agreement (3/3):     {rounds_with_full_agreement:3d} ({rounds_with_full_agreement/total_rounds*100:.1f}%)")
    print(f"   2/3 Majority:             {rounds_with_2_3_agreement:3d} ({rounds_with_2_3_agreement/total_rounds*100:.1f}%)")
    print(f"   Any Agreement (1+):       {rounds_with_agreement:3d} ({rounds_with_agreement/total_rounds*100:.1f}%)")
    print(f"   No Agreement (0/3):       {rounds_with_no_agreement:3d} ({rounds_with_no_agreement/total_rounds*100:.1f}%)")
    
    # Per-challenger pass rates
    print(f"\n📋 Per-Challenger Pass Rates:")
    for challenger in sorted(challenger_total_rounds.keys()):
        total = challenger_total_rounds[challenger]
        passed = challenger_pass_rates[challenger]
        rate = (passed / total * 100) if total > 0 else 0
        print(f"   {challenger:<20} {passed:3d}/{total:3d} ({rate:5.1f}%)")
    
    # Agreement patterns
    print(f"\n📊 Agreement Patterns (Frequency):")
    for pattern, count in agreement_patterns.most_common():
        percentage = (count / total_rounds * 100) if total_rounds > 0 else 0
        print(f"   {pattern:<30} {count:3d} rounds ({percentage:5.1f}%)")
    
    # Analyze final rounds only
    print(f"\n" + "=" * 80)
    print("🎯 FINAL ROUND ANALYSIS (Last Round of Each Assessment)")
    print("=" * 80)
    
    final_rounds = {}
    for detail in detailed_rounds:
        file = detail["file"]
        if file not in final_rounds or detail["round"] > final_rounds[file]["round"]:
            final_rounds[file] = detail
    
    final_round_stats = Counter([r["pattern"] for r in final_rounds.values()])
    final_total = len(final_rounds)
    
    final_full = sum(1 for r in final_rounds.values() if r["passed_count"] == 3)
    final_2_3 = sum(1 for r in final_rounds.values() if r["passed_count"] >= 2)
    final_any = sum(1 for r in final_rounds.values() if r["passed_count"] >= 1)
    final_none = sum(1 for r in final_rounds.values() if r["passed_count"] == 0)
    
    print(f"\nTotal Final Rounds: {final_total}")
    print(f"   Full Agreement (3/3):     {final_full:3d} ({final_full/final_total*100:.1f}%)")
    print(f"   2/3 Majority:             {final_2_3:3d} ({final_2_3/final_total*100:.1f}%)")
    print(f"   Any Agreement (1+):       {final_any:3d} ({final_any/final_total*100:.1f}%)")
    print(f"   No Agreement (0/3):       {final_none:3d} ({final_none/final_total*100:.1f}%)")
    
    print(f"\nFinal Round Patterns:")
    for pattern, count in final_round_stats.most_common():
        percentage = (count / final_total * 100) if final_total > 0 else 0
        print(f"   {pattern:<30} {count:3d} assessments ({percentage:5.1f}%)")
    
    # Key insights
    print(f"\n" + "=" * 80)
    print("💡 KEY INSIGHTS")
    print("=" * 80)
    
    if rounds_with_2_3_agreement / total_rounds < 0.3:
        print("⚠️  LOW AGREEMENT RATE: Challengers rarely reach 2/3 majority")
        print("   - This means the early termination mechanism is rarely triggered")
        print("   - Most assessments run all 3 revisions, increasing costs")
    
    if rounds_with_no_agreement / total_rounds > 0.5:
        print("⚠️  HIGH DISAGREEMENT: Over 50% of rounds have zero agreement")
        print("   - Challengers may have conflicting standards")
        print("   - Consider adjusting convergence threshold or challenger criteria")
    
    if final_2_3 / final_total < 0.2:
        print("⚠️  POOR FINAL CONVERGENCE: Less than 20% reach 2/3 majority in final round")
        print("   - System is not converging effectively")
        print("   - May need to adjust revision strategy or challenger prompts")
    
    return {
        "total_rounds": total_rounds,
        "rounds_with_full_agreement": rounds_with_full_agreement,
        "rounds_with_2_3_agreement": rounds_with_2_3_agreement,
        "rounds_with_agreement": rounds_with_agreement,
        "rounds_with_no_agreement": rounds_with_no_agreement,
        "challenger_pass_rates": dict(challenger_pass_rates),
        "challenger_total_rounds": dict(challenger_total_rounds),
        "agreement_patterns": dict(agreement_patterns),
        "final_round_stats": {
            "total": final_total,
            "full_agreement": final_full,
            "2_3_majority": final_2_3,
            "any_agreement": final_any,
            "no_agreement": final_none
        }
    }


if __name__ == "__main__":
    analyze_challenger_agreement()

