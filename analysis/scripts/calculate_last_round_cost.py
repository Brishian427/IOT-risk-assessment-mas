"""
Calculate Cost from Last Evaluation Round
Created: 2025-12-09
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import cost estimator directly
sys.path.insert(0, str(project_root / "scripts"))
from cost_estimator import (
    PRICING, TAVILY_COST_PER_SEARCH, TOKEN_USAGE,
    calculate_model_cost
)
from src.config import Config

def calculate_actual_cost_from_results(results_dir: str = "results") -> dict:
    """Calculate actual cost from the last batch evaluation"""
    
    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"Error: Results directory '{results_dir}' not found.")
        return {}
    
    # Get the most recent batch (assessments from 2025-12-09)
    result_files = sorted([
        f for f in results_path.glob("assessment_*.json")
        if "20251209" in f.name
    ])
    
    if not result_files:
        print("No results from 2025-12-09 found.")
        return {}
    
    print(f"📊 Analyzing {len(result_files)} assessments from last round (2025-12-09)...\n")
    
    total_cost = 0.0
    total_generator_cost = 0.0
    total_revision_cost = 0.0
    total_tavily_cost = 0.0
    
    breakdown = {
        "assessments": [],
        "summary": {}
    }
    
    for file_path in result_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            revision_count = data.get("metadata", {}).get("revision_count", 0) or data.get("output", {}).get("revision_count", 0)
            critiques = data.get("output", {}).get("critiques", [])
            conversation_log = data.get("conversation_log", [])
            
            # Count Tavily searches (challenger_b calls with citations)
            tavily_searches = 0
            for entry in conversation_log:
                if entry.get("stage") == "challenger_b":
                    # Estimate citations checked from extra field
                    citations_checked = entry.get("extra", {}).get("citations_checked", 0)
                    if citations_checked > 0:
                        tavily_searches += citations_checked
            
            # Calculate costs
            assessment_cost = 0.0
            
            # Generator Ensemble (9 models, runs once)
            gen_cost = 0.0
            gen_tokens = TOKEN_USAGE["generator"]
            for model_name in Config.GENERATOR_MODELS:
                cost = calculate_model_cost(
                    model_name,
                    gen_tokens["input"],
                    gen_tokens["output"]
                )
                gen_cost += cost
            
            assessment_cost += gen_cost
            total_generator_cost += gen_cost
            
            # Per revision cycle (0 to revision_count inclusive)
            revision_cycle_cost = 0.0
            for revision in range(revision_count + 1):
                cycle_cost = 0.0
                
                # Aggregator
                agg_tokens = TOKEN_USAGE["aggregator"]
                agg_cost = calculate_model_cost(
                    Config.AGGREGATOR_MODEL,
                    agg_tokens["input"],
                    agg_tokens["output"]
                )
                cycle_cost += agg_cost
                
                # Challenger A
                chall_a_tokens = TOKEN_USAGE["challenger_a"]
                chall_a_cost = calculate_model_cost(
                    Config.CHALLENGER_A_MODEL,
                    chall_a_tokens["input"],
                    chall_a_tokens["output"]
                )
                cycle_cost += chall_a_cost
                
                # Challenger B
                chall_b_tokens = TOKEN_USAGE["challenger_b"]
                chall_b_cost = calculate_model_cost(
                    Config.CHALLENGER_B_MODEL,
                    chall_b_tokens["input"],
                    chall_b_tokens["output"]
                )
                cycle_cost += chall_b_cost
                
                # Challenger C
                chall_c_tokens = TOKEN_USAGE["challenger_c"]
                chall_c_cost = calculate_model_cost(
                    Config.CHALLENGER_C_MODEL,
                    chall_c_tokens["input"],
                    chall_c_tokens["output"]
                )
                cycle_cost += chall_c_cost
                
                # Verifier
                ver_tokens = TOKEN_USAGE["verifier"]
                ver_cost = calculate_model_cost(
                    Config.VERIFIER_MODEL,
                    ver_tokens["input"],
                    ver_tokens["output"]
                )
                cycle_cost += ver_cost
                
                revision_cycle_cost += cycle_cost
            
            assessment_cost += revision_cycle_cost
            total_revision_cost += revision_cycle_cost
            
            # Tavily Search costs
            tavily_cost = tavily_searches * TAVILY_COST_PER_SEARCH
            assessment_cost += tavily_cost
            total_tavily_cost += tavily_cost
            
            total_cost += assessment_cost
            
            # Extract scenario name
            risk_input = data.get("input", {}).get("risk_scenario", "") or data.get("metadata", {}).get("risk_input", "")
            scenario_name = risk_input.split('\n')[0] if risk_input else "Unknown"
            if "Lifecycle Stage:" in scenario_name:
                lines = risk_input.split('\n')
                scenario_name = lines[1] if len(lines) > 1 else scenario_name
            
            breakdown["assessments"].append({
                "file": file_path.name,
                "scenario": scenario_name[:50],
                "revision_count": revision_count,
                "tavily_searches": tavily_searches,
                "cost": assessment_cost,
                "breakdown": {
                    "generator": gen_cost,
                    "revisions": revision_cycle_cost,
                    "tavily": tavily_cost
                }
            })
        
        except Exception as e:
            print(f"⚠️  Error processing {file_path.name}: {e}")
            continue
    
    breakdown["summary"] = {
        "total_assessments": len(breakdown["assessments"]),
        "total_cost_usd": total_cost,
        "generator_cost": total_generator_cost,
        "revision_cost": total_revision_cost,
        "tavily_cost": total_tavily_cost,
        "average_cost_per_assessment": total_cost / len(breakdown["assessments"]) if breakdown["assessments"] else 0,
        "total_revision_cycles": sum(a["revision_count"] + 1 for a in breakdown["assessments"]),
        "total_tavily_searches": sum(a["tavily_searches"] for a in breakdown["assessments"])
    }
    
    return breakdown


def print_cost_report(breakdown: dict):
    """Print formatted cost report"""
    
    if not breakdown or not breakdown.get("assessments"):
        print("No cost data available.")
        return
    
    summary = breakdown["summary"]
    
    print("=" * 80)
    print("💰 COST ANALYSIS - LAST EVALUATION ROUND (2025-12-09)")
    print("=" * 80)
    
    print(f"\n📊 Summary:")
    print(f"   Total Assessments: {summary['total_assessments']}")
    print(f"   Total Revision Cycles: {summary['total_revision_cycles']}")
    print(f"   Total Tavily Searches: {summary['total_tavily_searches']}")
    
    print(f"\n💵 Cost Breakdown:")
    print(f"   Generator Ensemble: ${summary['generator_cost']:.4f}")
    print(f"   Revision Cycles:    ${summary['revision_cost']:.4f}")
    print(f"   Tavily Searches:    ${summary['tavily_cost']:.4f}")
    print(f"   {'─' * 50}")
    print(f"   TOTAL COST:         ${summary['total_cost_usd']:.4f} USD")
    print(f"   Average per Assessment: ${summary['average_cost_per_assessment']:.4f} USD")
    
    print(f"\n📋 Per-Assessment Breakdown:")
    print(f"{'Scenario':<40} {'Revisions':<12} {'Tavily':<10} {'Cost (USD)':<12}")
    print("-" * 80)
    
    for assessment in breakdown["assessments"]:
        scenario_short = assessment["scenario"][:38]
        revisions = f"{assessment['revision_count']}"
        tavily = f"{assessment['tavily_searches']}"
        cost = f"${assessment['cost']:.4f}"
        print(f"{scenario_short:<40} {revisions:<12} {tavily:<10} {cost:<12}")
    
    print("=" * 80)


if __name__ == "__main__":
    breakdown = calculate_actual_cost_from_results()
    print_cost_report(breakdown)

