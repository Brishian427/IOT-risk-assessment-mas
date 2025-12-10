"""
Summarize Risk Assessment Scores for 11 Scenarios
Created: 2025-12-09
"""

import json
from pathlib import Path
from collections import defaultdict

# Get the 11 most recent assessment files
results_dir = Path("results")
files = sorted(results_dir.glob("assessment_iot_risk_20251209_22*.json"))

if len(files) < 11:
    files = sorted(results_dir.glob("assessment_iot_risk_20251209_*.json"))[-11:]

print("=" * 80)
print("📊 风险评估分数总结 - 11个场景")
print("=" * 80)
print()

scenarios_by_phase = {
    "Usage Phase": [],
    "End-of-Life (EOL)": []
}

for filepath in files[-11:]:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get scenario info
    scenario_text = (
        data.get('input', {}).get('risk_scenario', '') or 
        data.get('metadata', {}).get('risk_input', '')
    )
    
    # Extract lifecycle stage
    lifecycle_stage = "Unknown"
    risk_category = "Unknown"
    
    if scenario_text:
        lines = scenario_text.split('\n')
        for line in lines:
            if "Lifecycle Stage:" in line:
                lifecycle_stage = line.split("Lifecycle Stage:")[-1].strip()
            if "Risk Category:" in line:
                risk_category = line.split("Risk Category:")[-1].strip()
    
    # Get score
    synthesized_draft = data.get('output', {}).get('synthesized_draft')
    if synthesized_draft:
        score = synthesized_draft.get('score', 'N/A')
        revision_count = data.get('metadata', {}).get('revision_count', 0) or data.get('workflow_stats', {}).get('revision_count', 0)
        
        # Determine phase
        if "Usage" in lifecycle_stage or "Usage Phase" in lifecycle_stage:
            phase = "Usage Phase"
        elif "EOL" in lifecycle_stage or "End-of-Life" in lifecycle_stage:
            phase = "End-of-Life (EOL)"
        else:
            phase = "Unknown"
        
        # Extract scenario number from risk category or filename
        scenario_num = None
        # Map risk categories to scenario numbers
        category_to_num = {
            "Mass Data Inference": 1,
            "Remote Direct Control": 2,
            "Data Hacking & Breaching": 3,
            "User Awareness Risk": 4,
            "User Awareness / Legal & Compliance": 4,  # Alternative name
            "Lack of Continuous Updates": 5,
            "Cloud Dependence": 6,
            "Protocol Weaknesses": 8,
            "Data Privacy / Information Leakage": 10,
            "Environmental Toxicity": 11,
            "Physical Safety / Fire Hazard": 9,
        }
        
        # Try to match by category first
        for cat, num in category_to_num.items():
            if cat in risk_category:
                scenario_num = num
                break
        
        # If not found, try filename
        if scenario_num is None and "scenario_" in filepath.name:
            try:
                parts = filepath.name.split('_')
                for part in parts:
                    if part.isdigit():
                        scenario_num = int(part)
                        break
            except:
                pass
        
        scenarios_by_phase[phase].append({
            "file": filepath.name,
            "scenario_num": scenario_num,
            "risk_category": risk_category,
            "score": score,
            "revision_count": revision_count,
            "lifecycle_stage": lifecycle_stage
        })

# Sort by scenario number if available
for phase in scenarios_by_phase:
    scenarios_by_phase[phase].sort(key=lambda x: x.get('scenario_num') or 999)

# Print summary
print("📋 USAGE PHASE 场景 (使用阶段)")
print("=" * 80)
usage_scenarios = scenarios_by_phase["Usage Phase"]
if usage_scenarios:
    print(f"{'场景':<6} {'风险类别':<40} {'分数':<8} {'修订轮数':<10}")
    print("-" * 80)
    for i, s in enumerate(usage_scenarios, 1):
        scenario_label = f"场景{s['scenario_num']}" if s['scenario_num'] else f"场景{i}"
        category = s['risk_category'][:38] if len(s['risk_category']) > 38 else s['risk_category']
        print(f"{scenario_label:<6} {category:<40} {s['score']}/5{'':<4} {s['revision_count']:<10}")
    
    # Calculate average
    scores = [s['score'] for s in usage_scenarios if isinstance(s['score'], int)]
    if scores:
        avg_score = sum(scores) / len(scores)
        print("-" * 80)
        print(f"{'平均分数':<48} {avg_score:.2f}/5")
        print(f"{'场景数量':<48} {len(usage_scenarios)}")
else:
    print("   (无)")

print()
print("📋 END-OF-LIFE (EOL) 场景 (生命周期结束阶段)")
print("=" * 80)
eol_scenarios = scenarios_by_phase["End-of-Life (EOL)"]
if eol_scenarios:
    print(f"{'场景':<6} {'风险类别':<40} {'分数':<8} {'修订轮数':<10}")
    print("-" * 80)
    for i, s in enumerate(eol_scenarios, 1):
        scenario_label = f"场景{s['scenario_num']}" if s['scenario_num'] else f"场景{i}"
        category = s['risk_category'][:38] if len(s['risk_category']) > 38 else s['risk_category']
        print(f"{scenario_label:<6} {category:<40} {s['score']}/5{'':<4} {s['revision_count']:<10}")
    
    # Calculate average
    scores = [s['score'] for s in eol_scenarios if isinstance(s['score'], int)]
    if scores:
        avg_score = sum(scores) / len(scores)
        print("-" * 80)
        print(f"{'平均分数':<48} {avg_score:.2f}/5")
        print(f"{'场景数量':<48} {len(eol_scenarios)}")
else:
    print("   (无)")

print()
print("=" * 80)
print("📊 总体统计")
print("=" * 80)

all_scores = []
for phase_scenarios in scenarios_by_phase.values():
    for s in phase_scenarios:
        if isinstance(s['score'], int):
            all_scores.append(s['score'])

if all_scores:
    print(f"总场景数: {len(all_scores)}")
    print(f"总体平均分数: {sum(all_scores)/len(all_scores):.2f}/5")
    print(f"最高分数: {max(all_scores)}/5")
    print(f"最低分数: {min(all_scores)}/5")
    print(f"分数分布: {dict((i, all_scores.count(i)) for i in range(1, 6))}")

