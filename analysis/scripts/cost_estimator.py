"""
Cost Estimator for Multi-Agent System
Created: 2025-01-XX
Estimates the cost per operation based on model pricing and typical token usage
"""

# Pricing per million tokens (as of 2025)
# Input/Output pricing where applicable

PRICING = {
    # OpenAI
    "gpt-4o": {
        "input": 2.50,  # $2.50 per million tokens
        "output": 10.00,  # $10.00 per million tokens
    },
    "gpt-4o-mini": {
        "input": 0.15,  # $0.15 per million tokens
        "output": 0.60,  # $0.60 per million tokens
    },
    "o1-mini": {
        "input": 3.00,  # $3.00 per million tokens
        "output": 12.00,  # $12.00 per million tokens
    },
    # Anthropic
    "claude-3-5-sonnet-latest": {
        "input": 3.00,  # $3.00 per million tokens
        "output": 15.00,  # $15.00 per million tokens
    },
    "claude-3-opus-20240229": {
        "input": 15.00,  # $15.00 per million tokens
        "output": 75.00,  # $75.00 per million tokens
    },
    # Google
    "gemini-1.5-pro": {
        "input": 1.25,  # $1.25 per million tokens
        "output": 5.00,  # $5.00 per million tokens
    },
    "gemini-pro": {
        "input": 0.50,  # $0.50 per million tokens (free tier available)
        "output": 1.50,  # $1.50 per million tokens
    },
    # DeepSeek
    "deepseek-chat": {
        "input": 0.14,  # $0.14 per million tokens
        "output": 0.28,  # $0.28 per million tokens
    },
    # Groq (Llama)
    "llama-3.3-70b-versatile": {
        "input": 0.00,  # Free tier (rate limited)
        "output": 0.00,
    },
    # Mistral
    "mistral-large-latest": {
        "input": 2.70,  # $2.70 per million tokens
        "output": 8.10,  # $8.10 per million tokens
    },
}

# Tavily Search API
TAVILY_COST_PER_SEARCH = 0.001  # $0.001 per search (estimated)

# Typical token usage per operation (estimated)
TOKEN_USAGE = {
    "generator": {
        "input": 2000,  # Risk input + prompt template
        "output": 1500,  # JSON response with reasoning trace
    },
    "aggregator": {
        "input": 15000,  # 9 assessments formatted
        "output": 2000,  # Synthesized assessment
    },
    "challenger_a": {
        "input": 4000,  # Synthesized draft + prompt
        "output": 800,  # Critique JSON
    },
    "challenger_b": {
        "input": 6000,  # Assessment + search results + prompt
        "output": 1000,  # Critique JSON
    },
    "challenger_c": {
        "input": 4000,  # Synthesized draft + prompt
        "output": 800,  # Critique JSON
    },
    "verifier": {
        "input": 5000,  # Assessment + critiques + prompt
        "output": 500,  # Routing decision JSON
    },
}


def calculate_model_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for a single model call"""
    if model_name not in PRICING:
        # Unknown model - estimate based on average
        return (input_tokens * 2.0 / 1_000_000) + (output_tokens * 8.0 / 1_000_000)
    
    pricing = PRICING[model_name]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def estimate_single_operation_cost(max_revisions: int = 3, citations_per_assessment: int = 4) -> dict:
    """
    Estimate cost for one complete risk assessment operation
    
    Args:
        max_revisions: Maximum number of revision cycles (default 3)
        citations_per_assessment: Average number of citations to verify (default 4)
    
    Returns:
        Dictionary with detailed cost breakdown
    """
    from src.config import Config
    
    total_cost = 0.0
    breakdown = {
        "generator_ensemble": {},
        "aggregator": {},
        "challengers": {},
        "verifier": {},
        "tavily_search": {},
        "per_revision": [],
        "total": 0.0,
    }
    
    # Generator Ensemble (9 models, runs once)
    gen_tokens = TOKEN_USAGE["generator"]
    gen_cost = 0.0
    gen_details = {}
    
    for model_name in Config.GENERATOR_MODELS:
        cost = calculate_model_cost(
            model_name,
            gen_tokens["input"],
            gen_tokens["output"]
        )
        gen_cost += cost
        gen_details[model_name] = cost
    
    breakdown["generator_ensemble"] = {
        "models": gen_details,
        "total": gen_cost,
        "calls": len(Config.GENERATOR_MODELS)
    }
    total_cost += gen_cost
    
    # Per revision cycle
    for revision in range(max_revisions + 1):  # 0 to max_revisions (inclusive)
        cycle_cost = 0.0
        cycle_breakdown = {}
        
        # Aggregator (runs each revision cycle)
        agg_tokens = TOKEN_USAGE["aggregator"]
        agg_cost = calculate_model_cost(
            Config.AGGREGATOR_MODEL,
            agg_tokens["input"],
            agg_tokens["output"]
        )
        cycle_cost += agg_cost
        cycle_breakdown["aggregator"] = agg_cost
        
        # Challenger A
        chall_a_tokens = TOKEN_USAGE["challenger_a"]
        chall_a_cost = calculate_model_cost(
            Config.CHALLENGER_A_MODEL,
            chall_a_tokens["input"],
            chall_a_tokens["output"]
        )
        cycle_cost += chall_a_cost
        cycle_breakdown["challenger_a"] = chall_a_cost
        
        # Challenger B (includes Tavily searches)
        chall_b_tokens = TOKEN_USAGE["challenger_b"]
        chall_b_cost = calculate_model_cost(
            Config.CHALLENGER_B_MODEL,
            chall_b_tokens["input"],
            chall_b_tokens["output"]
        )
        tavily_cost = citations_per_assessment * TAVILY_COST_PER_SEARCH
        cycle_cost += chall_b_cost + tavily_cost
        cycle_breakdown["challenger_b"] = {
            "model": chall_b_cost,
            "tavily_searches": tavily_cost,
            "searches_count": citations_per_assessment,
        }
        
        # Challenger C
        chall_c_tokens = TOKEN_USAGE["challenger_c"]
        chall_c_cost = calculate_model_cost(
            Config.CHALLENGER_C_MODEL,
            chall_c_tokens["input"],
            chall_c_tokens["output"]
        )
        cycle_cost += chall_c_cost
        cycle_breakdown["challenger_c"] = chall_c_cost
        
        # Verifier
        ver_tokens = TOKEN_USAGE["verifier"]
        ver_cost = calculate_model_cost(
            Config.VERIFIER_MODEL,
            ver_tokens["input"],
            ver_tokens["output"]
        )
        cycle_cost += ver_cost
        cycle_breakdown["verifier"] = ver_cost
        
        breakdown["per_revision"].append({
            "revision": revision,
            "cost": cycle_cost,
            "breakdown": cycle_breakdown
        })
        total_cost += cycle_cost
    
    breakdown["total"] = total_cost
    
    # Summary statistics
    breakdown["summary"] = {
        "total_operations": max_revisions + 1,
        "generator_calls": len(Config.GENERATOR_MODELS),
        "total_llm_calls": (
            len(Config.GENERATOR_MODELS) +  # Generator ensemble
            (max_revisions + 1) * 5  # 5 agents per revision (agg + 3 challengers + verifier)
        ),
        "total_tavily_searches": citations_per_assessment * (max_revisions + 1),
        "average_cost_per_revision": sum(r["cost"] for r in breakdown["per_revision"]) / (max_revisions + 1),
    }
    
    return breakdown


def print_cost_breakdown(breakdown: dict, exchange_rate: float = 7.25):
    """Print formatted cost breakdown"""
    print("=" * 80)
    print("COST ESTIMATION FOR ONE RISK ASSESSMENT OPERATION")
    print("=" * 80)
    print(f"Exchange Rate: 1 USD = {exchange_rate} CNY")
    print()
    
    # Generator Ensemble
    print("📊 GENERATOR ENSEMBLE (Runs Once)")
    print("-" * 80)
    gen_total = breakdown["generator_ensemble"]["total"]
    print(f"Total Cost: ${gen_total:.4f} (¥{gen_total * exchange_rate:.2f})")
    print(f"Models: {breakdown['generator_ensemble']['calls']}")
    print("\nPer Model Breakdown:")
    for model, cost in breakdown["generator_ensemble"]["models"].items():
        print(f"  • {model:30s}: ${cost:.4f} (¥{cost * exchange_rate:.2f})")
    print()
    
    # Per Revision Cycle
    print("🔄 REVISION CYCLES")
    print("-" * 80)
    for rev_data in breakdown["per_revision"]:
        rev_num = rev_data["revision"]
        rev_cost = rev_data["cost"]
        print(f"\nRevision {rev_num}: ${rev_cost:.4f} (¥{rev_cost * exchange_rate:.2f})")
        print("  Breakdown:")
        print(f"    • Aggregator:        ${rev_data['breakdown']['aggregator']:.4f} (¥{rev_data['breakdown']['aggregator'] * exchange_rate:.2f})")
        print(f"    • Challenger A:      ${rev_data['breakdown']['challenger_a']:.4f} (¥{rev_data['breakdown']['challenger_a'] * exchange_rate:.2f})")
        chall_b = rev_data['breakdown']['challenger_b']
        if isinstance(chall_b, dict):
            print(f"    • Challenger B:      ${chall_b['model']:.4f} (¥{chall_b['model'] * exchange_rate:.2f})")
            print(f"      - Tavily Searches: ${chall_b['tavily_searches']:.4f} (¥{chall_b['tavily_searches'] * exchange_rate:.2f}) ({chall_b['searches_count']} searches)")
        else:
            print(f"    • Challenger B:      ${chall_b:.4f} (¥{chall_b * exchange_rate:.2f})")
        print(f"    • Challenger C:      ${rev_data['breakdown']['challenger_c']:.4f} (¥{rev_data['breakdown']['challenger_c'] * exchange_rate:.2f})")
        print(f"    • Verifier:          ${rev_data['breakdown']['verifier']:.4f} (¥{rev_data['breakdown']['verifier'] * exchange_rate:.2f})")
    
    # Summary
    print()
    print("=" * 80)
    print("📈 SUMMARY")
    print("=" * 80)
    summary = breakdown["summary"]
    total_usd = breakdown['total']
    total_cny = total_usd * exchange_rate
    print(f"Total Cost:                    ${total_usd:.4f} (¥{total_cny:.2f})")
    print(f"Total LLM API Calls:           {summary['total_llm_calls']}")
    print(f"Total Tavily Searches:         {summary['total_tavily_searches']}")
    avg_rev_usd = summary['average_cost_per_revision']
    print(f"Average Cost per Revision:     ${avg_rev_usd:.4f} (¥{avg_rev_usd * exchange_rate:.2f})")
    print()
    print(f"Cost Breakdown:")
    gen_total = breakdown['generator_ensemble']['total']
    print(f"  • Generator Ensemble:       ${gen_total:.4f} (¥{gen_total * exchange_rate:.2f}) ({gen_total/total_usd*100:.1f}%)")
    revision_total = sum(r["cost"] for r in breakdown["per_revision"])
    print(f"  • Revision Cycles:          ${revision_total:.4f} (¥{revision_total * exchange_rate:.2f}) ({revision_total/total_usd*100:.1f}%)")
    print()
    print("=" * 80)


if __name__ == "__main__":
    # Estimate with default settings (3 max revisions, 4 citations)
    # Exchange rate: 1 USD = 7.25 CNY (approximate as of 2025)
    exchange_rate = 7.25
    breakdown = estimate_single_operation_cost(max_revisions=3, citations_per_assessment=4)
    print_cost_breakdown(breakdown, exchange_rate=exchange_rate)
    
    print("\n" + "=" * 80)
    print("💡 COST OPTIMIZATION SCENARIOS")
    print("=" * 80)
    print()
    
    # Scenario 1: No revisions (perfect first pass)
    print("Scenario 1: No Revisions (Perfect First Pass)")
    breakdown_0 = estimate_single_operation_cost(max_revisions=0, citations_per_assessment=4)
    cost_0_usd = breakdown_0['total']
    cost_0_cny = cost_0_usd * exchange_rate
    savings_usd = breakdown['total'] - cost_0_usd
    savings_cny = savings_usd * exchange_rate
    print(f"  Cost: ${cost_0_usd:.4f} (¥{cost_0_cny:.2f}) - Saves ${savings_usd:.4f} (¥{savings_cny:.2f})")
    print()
    
    # Scenario 2: Fewer citations
    print("Scenario 2: Fewer Citations (2 instead of 4)")
    breakdown_2 = estimate_single_operation_cost(max_revisions=3, citations_per_assessment=2)
    cost_2_usd = breakdown_2['total']
    cost_2_cny = cost_2_usd * exchange_rate
    savings_2_usd = breakdown['total'] - cost_2_usd
    savings_2_cny = savings_2_usd * exchange_rate
    print(f"  Cost: ${cost_2_usd:.4f} (¥{cost_2_cny:.2f}) - Saves ${savings_2_usd:.4f} (¥{savings_2_cny:.2f})")
    print()
    
    # Scenario 3: Single revision
    print("Scenario 3: Single Revision Cycle")
    breakdown_1 = estimate_single_operation_cost(max_revisions=1, citations_per_assessment=4)
    cost_1_usd = breakdown_1['total']
    cost_1_cny = cost_1_usd * exchange_rate
    savings_1_usd = breakdown['total'] - cost_1_usd
    savings_1_cny = savings_1_usd * exchange_rate
    print(f"  Cost: ${cost_1_usd:.4f} (¥{cost_1_cny:.2f}) - Saves ${savings_1_usd:.4f} (¥{savings_1_cny:.2f})")
    print()

