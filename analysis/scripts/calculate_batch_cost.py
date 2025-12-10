"""
Calculate cost for the latest batch of 11 scenarios
Created: 2025-12-09
"""

import json
from pathlib import Path

# Cost per operation (from cost_estimator.py)
GEN_COST = 0.1332  # Generator ensemble (9 models)
CYCLE_COST = 0.136  # Per revision cycle (aggregator + 3 challengers + verifier)

# Get the 11 most recent assessment files from today
results_dir = Path("results")
files = sorted(results_dir.glob("assessment_iot_risk_20251209_22*.json"))

if len(files) < 11:
    print(f"⚠️  只找到 {len(files)} 个文件，预期11个")
    files = sorted(results_dir.glob("assessment_iot_risk_20251209_*.json"))[-11:]

print("=" * 80)
print("💰 批量评估成本计算 (11个场景)")
print("=" * 80)
print(f"\n找到 {len(files)} 个评估文件:\n")

total_cost = 0.0
total_revisions = 0

for i, filepath in enumerate(files[-11:], 1):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get revision count
    revision_count = (
        data.get('metadata', {}).get('revision_count', 0) or
        data.get('workflow_stats', {}).get('revision_count', 0)
    )
    cycles = revision_count + 1  # Initial + revisions
    
    # Calculate cost
    assessment_cost = GEN_COST + (CYCLE_COST * cycles)
    total_cost += assessment_cost
    total_revisions += revision_count
    
    # Get scenario name
    scenario = data.get('input', {}).get('risk_scenario', '') or data.get('metadata', {}).get('risk_input', '')
    scenario_name = scenario.split('\n')[0][:40] if scenario else filepath.name
    
    print(f"{i:2d}. {filepath.name}")
    print(f"    场景: {scenario_name}")
    print(f"    修订轮数: {revision_count} (总循环: {cycles})")
    print(f"    成本: ${assessment_cost:.4f} USD")
    print()

print("=" * 80)
print("📊 成本汇总")
print("=" * 80)
print(f"\n总评估数: 11")
print(f"总修订轮数: {total_revisions}")
print(f"平均修订轮数: {total_revisions/11:.1f}")
print(f"\n💵 总成本:")
print(f"   ${total_cost:.4f} USD")
print(f"   ¥{total_cost * 7.2:.2f} CNY (按汇率 7.2)")
print(f"\n平均每个场景: ${total_cost/11:.4f} USD (¥{total_cost*7.2/11:.2f} CNY)")

