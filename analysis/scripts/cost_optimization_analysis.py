"""
Cost Optimization Analysis and Recommendations
Created: 2025-12-09
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

from cost_estimator import (
    PRICING, TAVILY_COST_PER_SEARCH, TOKEN_USAGE,
    calculate_model_cost
)
from src.config import Config

def analyze_current_cost():
    """Analyze current cost structure"""
    print("=" * 80)
    print("💰 CURRENT COST ANALYSIS")
    print("=" * 80)
    
    # Generator Ensemble
    gen_tokens = TOKEN_USAGE["generator"]
    gen_cost = 0.0
    gen_details = {}
    
    print("\n📊 Generator Ensemble (9 models):")
    for model_name in Config.GENERATOR_MODELS:
        cost = calculate_model_cost(
            model_name,
            gen_tokens["input"],
            gen_tokens["output"]
        )
        gen_cost += cost
        gen_details[model_name] = cost
        # Use average pricing for unknown models
        if model_name not in PRICING:
            print(f"   {model_name:<30} ${cost:.6f} (estimated)")
        else:
            print(f"   {model_name:<30} ${cost:.6f}")
    
    print(f"   {'─' * 50}")
    print(f"   Total Generator Cost: ${gen_cost:.4f}")
    
    # Per revision cycle (using current models)
    print("\n📊 Per Revision Cycle (4 cycles = initial + 3 revisions):")
    cycle_cost = 0.0
    
    # Aggregator
    agg_tokens = TOKEN_USAGE["aggregator"]
    agg_cost = calculate_model_cost(
        Config.AGGREGATOR_MODEL,
        agg_tokens["input"],
        agg_tokens["output"]
    )
    cycle_cost += agg_cost
    print(f"   Aggregator ({Config.AGGREGATOR_MODEL}):     ${agg_cost:.6f}")
    
    # Challenger A
    chall_a_tokens = TOKEN_USAGE["challenger_a"]
    chall_a_cost = calculate_model_cost(
        Config.CHALLENGER_A_MODEL,
        chall_a_tokens["input"],
        chall_a_tokens["output"]
    )
    cycle_cost += agg_cost
    print(f"   Challenger A ({Config.CHALLENGER_A_MODEL}):  ${chall_a_cost:.6f}")
    
    # Challenger B
    chall_b_tokens = TOKEN_USAGE["challenger_b"]
    chall_b_cost = calculate_model_cost(
        Config.CHALLENGER_B_MODEL,
        chall_b_tokens["input"],
        chall_b_tokens["output"]
    )
    cycle_cost += chall_b_cost
    print(f"   Challenger B ({Config.CHALLENGER_B_MODEL}):  ${chall_b_cost:.6f}")
    
    # Challenger C
    chall_c_tokens = TOKEN_USAGE["challenger_c"]
    chall_c_cost = calculate_model_cost(
        Config.CHALLENGER_C_MODEL,
        chall_c_tokens["input"],
        chall_c_tokens["output"]
    )
    cycle_cost += chall_c_cost
    print(f"   Challenger C ({Config.CHALLENGER_C_MODEL}):  ${chall_c_cost:.6f}")
    
    # Verifier
    ver_tokens = TOKEN_USAGE["verifier"]
    ver_cost = calculate_model_cost(
        Config.VERIFIER_MODEL,
        ver_tokens["input"],
        ver_tokens["output"]
    )
    cycle_cost += ver_cost
    print(f"   Verifier ({Config.VERIFIER_MODEL}):         ${ver_cost:.6f}")
    
    print(f"   {'─' * 50}")
    print(f"   Per Cycle Cost: ${cycle_cost:.6f}")
    print(f"   4 Cycles Total: ${cycle_cost * 4:.4f}")
    
    total_cost = gen_cost + (cycle_cost * 4)
    print(f"\n💵 TOTAL COST PER ASSESSMENT: ${total_cost:.4f}")
    
    return {
        "generator": gen_cost,
        "per_cycle": cycle_cost,
        "total": total_cost
    }


def analyze_optimization_options():
    """Analyze different optimization strategies"""
    print("\n" + "=" * 80)
    print("🔧 COST OPTIMIZATION OPTIONS")
    print("=" * 80)
    
    gen_tokens = TOKEN_USAGE["generator"]
    agg_tokens = TOKEN_USAGE["aggregator"]
    chall_tokens = TOKEN_USAGE["challenger_a"]
    ver_tokens = TOKEN_USAGE["verifier"]
    
    # Option 1: Use gpt-4o-mini for all challengers/aggregator/verifier
    print("\n📋 Option 1: Use gpt-4o-mini for Aggregator, Challengers, Verifier")
    print("   (Keep Generator Ensemble as-is)")
    
    opt1_gen = sum(
        calculate_model_cost(m, gen_tokens["input"], gen_tokens["output"])
        for m in Config.GENERATOR_MODELS
    )
    
    opt1_cycle = (
        calculate_model_cost("gpt-4o-mini", agg_tokens["input"], agg_tokens["output"]) +
        calculate_model_cost("gpt-4o-mini", chall_tokens["input"], chall_tokens["output"]) * 3 +
        calculate_model_cost("gpt-4o-mini", ver_tokens["input"], ver_tokens["output"])
    )
    
    opt1_total = opt1_gen + (opt1_cycle * 4)
    savings1 = 0.6772 - opt1_total
    print(f"   Generator: ${opt1_gen:.4f}")
    print(f"   4 Cycles:  ${opt1_cycle * 4:.4f}")
    print(f"   Total:     ${opt1_total:.4f}")
    print(f"   Savings:   ${savings1:.4f} ({savings1/0.6772*100:.1f}% reduction)")
    
    # Option 2: Reduce Generator Ensemble to 5 models (keep best performers)
    print("\n📋 Option 2: Reduce Generator Ensemble to 5 models")
    print("   (Use: gpt-4o, gpt-4o-mini, gpt-3.5-turbo, gpt-4o-mini-2024-11-20, gpt-4o-2024-08-06)")
    
    opt2_models = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
        "gpt-4o-mini-2024-11-20",
        "gpt-4o-2024-08-06"
    ]
    opt2_gen = sum(
        calculate_model_cost(m, gen_tokens["input"], gen_tokens["output"])
        for m in opt2_models
    )
    opt2_cycle = opt1_cycle  # Same as Option 1
    opt2_total = opt2_gen + (opt2_cycle * 4)
    savings2 = 0.6772 - opt2_total
    print(f"   Generator: ${opt2_gen:.4f}")
    print(f"   4 Cycles:  ${opt2_cycle * 4:.4f}")
    print(f"   Total:     ${opt2_total:.4f}")
    print(f"   Savings:   ${savings2:.4f} ({savings2/0.6772*100:.1f}% reduction)")
    
    # Option 3: Combine Option 1 + 2 + Reduce MAX_REVISIONS to 2
    print("\n📋 Option 3: Option 1 + 2 + Reduce MAX_REVISIONS to 2")
    print("   (5 generators, gpt-4o-mini for all others, max 2 revisions = 3 cycles)")
    
    opt3_gen = opt2_gen
    opt3_cycle = opt1_cycle
    opt3_total = opt3_gen + (opt3_cycle * 3)  # 3 cycles instead of 4
    savings3 = 0.6772 - opt3_total
    print(f"   Generator: ${opt3_gen:.4f}")
    print(f"   3 Cycles:  ${opt3_cycle * 3:.4f}")
    print(f"   Total:     ${opt3_total:.4f}")
    print(f"   Savings:   ${savings3:.4f} ({savings3/0.6772*100:.1f}% reduction)")
    
    # Option 4: Use DeepSeek for Challenger B (cheapest option)
    print("\n📋 Option 4: Use DeepSeek for Challenger B (Citation Verification)")
    print("   (DeepSeek is 18x cheaper than gpt-4o)")
    
    opt4_gen = opt2_gen
    opt4_cycle = (
        calculate_model_cost("gpt-4o-mini", agg_tokens["input"], agg_tokens["output"]) +
        calculate_model_cost("gpt-4o-mini", chall_tokens["input"], chall_tokens["output"]) * 2 +
        calculate_model_cost("deepseek-chat", TOKEN_USAGE["challenger_b"]["input"], TOKEN_USAGE["challenger_b"]["output"]) +
        calculate_model_cost("gpt-4o-mini", ver_tokens["input"], ver_tokens["output"])
    )
    opt4_total = opt4_gen + (opt4_cycle * 3)  # 3 cycles
    savings4 = 0.6772 - opt4_total
    print(f"   Generator: ${opt4_gen:.4f}")
    print(f"   3 Cycles:  ${opt4_cycle * 3:.4f}")
    print(f"   Total:     ${opt4_total:.4f}")
    print(f"   Savings:   ${savings4:.4f} ({savings4/0.6772*100:.1f}% reduction)")
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Current Cost:        ${0.6772:.4f} per assessment")
    print(f"Option 1:            ${opt1_total:.4f} ({savings1/0.6772*100:+.1f}%)")
    print(f"Option 2:            ${opt2_total:.4f} ({savings2/0.6772*100:+.1f}%)")
    print(f"Option 3:            ${opt3_total:.4f} ({savings3/0.6772*100:+.1f}%) ⭐ BEST")
    print(f"Option 4:            ${opt4_total:.4f} ({savings4/0.6772*100:+.1f}%)")
    
    print("\n💡 RECOMMENDATIONS:")
    print("   1. Use gpt-4o-mini for Aggregator, Challengers, Verifier (16x cheaper)")
    print("   2. Reduce Generator Ensemble to 5 models (maintains diversity)")
    print("   3. Reduce MAX_REVISIONS to 2 (with 2/3 majority convergence, often sufficient)")
    print("   4. Consider DeepSeek for Challenger B if API is stable")
    print("   5. Early termination with 2/3 majority already implemented (will save costs)")
    
    return {
        "current": 0.6772,
        "option1": opt1_total,
        "option2": opt2_total,
        "option3": opt3_total,
        "option4": opt4_total
    }


if __name__ == "__main__":
    current = analyze_current_cost()
    options = analyze_optimization_options()

