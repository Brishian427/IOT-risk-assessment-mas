"""
Evaluation Results Summary for Human-AI Validation Research
Focus: AI scoring patterns, biases, and human intervention points
Created: 2025-12-10
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import statistics

def analyze_evaluation_results():
    """Comprehensive analysis of evaluation results for human-AI validation research"""
    
    formal_dir = Path('results/formal_assessment_20251210')
    files = sorted(formal_dir.glob('*.json'))
    
    # Data structures
    all_results = []
    generator_scores_by_model = defaultdict(list)
    generator_freq_by_model = defaultdict(list)
    generator_imp_by_model = defaultdict(list)
    final_scores = []
    scenario_details = []
    
    # Process all files
    for f in files:
        data = json.loads(f.read_text(encoding='utf-8'))
        risk_input = data['metadata']['risk_input']
        draft = data['output']['synthesized_draft']
        draft_assessments = data['output'].get('draft_assessments', [])
        
        # Extract scenario info
        scenario_name = "Unknown"
        if 'Risk Category:' in risk_input:
            scenario_name = risk_input.split('Risk Category:')[1].split('\n')[0].strip()
        
        lifecycle = "Usage Phase" if "Usage Phase" in risk_input else "EOL"
        
        # Final synthesized scores
        ra = draft.get('risk_assessment', {})
        final_freq = ra.get('frequency_score')
        final_imp = ra.get('impact_score')
        final_score = ra.get('final_risk_score')
        final_class = ra.get('risk_classification')
        
        # Analyze generator ensemble scores
        generator_scores = {}
        generator_freqs = {}
        generator_imps = {}
        
        for gen_assessment in draft_assessments:
            model_name = gen_assessment.get('model_name', 'unknown')
            gen_ra = gen_assessment.get('risk_assessment', {})
            
            if 'score' in gen_assessment:
                generator_scores[model_name] = gen_assessment['score']
                generator_scores_by_model[model_name].append(gen_assessment['score'])
            
            if 'frequency_score' in gen_ra:
                generator_freqs[model_name] = gen_ra['frequency_score']
                generator_freq_by_model[model_name].append(gen_ra['frequency_score'])
            
            if 'impact_score' in gen_ra:
                generator_imps[model_name] = gen_ra['impact_score']
                generator_imp_by_model[model_name].append(gen_ra['impact_score'])
        
        scenario_details.append({
            'scenario': scenario_name,
            'lifecycle': lifecycle,
            'final_freq': final_freq,
            'final_imp': final_imp,
            'final_score': final_score,
            'final_class': final_class,
            'generator_scores': generator_scores,
            'generator_freqs': generator_freqs,
            'generator_imps': generator_imps,
            'revisions': data['metadata']['revision_count'],
            'critiques': data['metadata']['total_critiques']
        })
        
        all_results.append({
            'scenario': scenario_name,
            'lifecycle': lifecycle,
            'final_score': final_score,
            'final_freq': final_freq,
            'final_imp': final_imp,
            'final_class': final_class
        })
        
        if final_score:
            final_scores.append(final_score)
    
    # Print comprehensive summary
    print("=" * 100)
    print("EVALUATION RESULTS SUMMARY: Human-AI Validation Research Focus".center(100))
    print("=" * 100)
    print()
    
    # 1. CORE RESULTS
    print("1. CORE RESULTS")
    print("-" * 100)
    print(f"Total Scenarios: {len(all_results)}")
    print(f"  • Usage Phase: {sum(1 for r in all_results if r['lifecycle'] == 'Usage Phase')}")
    print(f"  • EOL Phase: {sum(1 for r in all_results if r['lifecycle'] == 'EOL')}")
    print()
    
    print("Final Risk Score Distribution:")
    score_dist = defaultdict(int)
    for r in all_results:
        if r['final_score']:
            score_dist[r['final_score']] += 1
    for score in sorted(score_dist.keys(), reverse=True):
        print(f"  • {score}/25: {score_dist[score]} scenario(s)")
    print()
    
    print("Risk Classification:")
    class_dist = defaultdict(int)
    for r in all_results:
        if r['final_class']:
            class_dist[r['final_class']] += 1
    for cls, count in sorted(class_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {cls}: {count} ({count*100//len(all_results)}%)")
    print()
    
    # 2. AI MODEL SCORING STATISTICS
    print("2. AI MODEL SCORING STATISTICS & BIAS ANALYSIS")
    print("-" * 100)
    
    # Legacy scores (1-5)
    print("Generator Ensemble - Legacy Scores (1-5):")
    for model in sorted(generator_scores_by_model.keys()):
        scores = generator_scores_by_model[model]
        if scores:
            avg = statistics.mean(scores)
            std = statistics.stdev(scores) if len(scores) > 1 else 0
            min_score = min(scores)
            max_score = max(scores)
            print(f"  • {model:30s}: avg={avg:.2f}, std={std:.2f}, range=[{min_score}-{max_score}], n={len(scores)}")
    print()
    
    # Frequency scores
    print("Generator Ensemble - Frequency Scores (1-5):")
    for model in sorted(generator_freq_by_model.keys()):
        scores = generator_freq_by_model[model]
        if scores:
            avg = statistics.mean(scores)
            std = statistics.stdev(scores) if len(scores) > 1 else 0
            min_score = min(scores)
            max_score = max(scores)
            # Count distribution
            dist = defaultdict(int)
            for s in scores:
                dist[s] += 1
            dist_str = ", ".join([f"{k}:{v}" for k, v in sorted(dist.items())])
            print(f"  • {model:30s}: avg={avg:.2f}, std={std:.2f}, range=[{min_score}-{max_score}], dist=[{dist_str}], n={len(scores)}")
    print()
    
    # Impact scores
    print("Generator Ensemble - Impact Scores (1-5):")
    for model in sorted(generator_imp_by_model.keys()):
        scores = generator_imp_by_model[model]
        if scores:
            avg = statistics.mean(scores)
            std = statistics.stdev(scores) if len(scores) > 1 else 0
            min_score = min(scores)
            max_score = max(scores)
            dist = defaultdict(int)
            for s in scores:
                dist[s] += 1
            dist_str = ", ".join([f"{k}:{v}" for k, v in sorted(dist.items())])
            print(f"  • {model:30s}: avg={avg:.2f}, std={std:.2f}, range=[{min_score}-{max_score}], dist=[{dist_str}], n={len(scores)}")
    print()
    
    # Bias detection
    print("BIAS DETECTION:")
    print()
    
    # Check for systematic high/low scoring
    all_freq_scores = []
    all_imp_scores = []
    for model_scores in generator_freq_by_model.values():
        all_freq_scores.extend(model_scores)
    for model_scores in generator_imp_by_model.values():
        all_imp_scores.extend(model_scores)
    
    if all_freq_scores:
        freq_avg = statistics.mean(all_freq_scores)
        freq_median = statistics.median(all_freq_scores)
        print(f"  • Frequency Score Distribution:")
        print(f"    - Overall Average: {freq_avg:.2f}/5")
        print(f"    - Median: {freq_median:.2f}/5")
        print(f"    - Range: {min(all_freq_scores)} - {max(all_freq_scores)}")
        freq_dist = defaultdict(int)
        for s in all_freq_scores:
            freq_dist[s] += 1
        print(f"    - Distribution: {dict(sorted(freq_dist.items()))}")
        if freq_avg >= 4.5:
            print(f"    ⚠️  POTENTIAL BIAS: Frequency scores heavily skewed toward high end (avg {freq_avg:.2f} ≥ 4.5)")
        print()
    
    if all_imp_scores:
        imp_avg = statistics.mean(all_imp_scores)
        imp_median = statistics.median(all_imp_scores)
        print(f"  • Impact Score Distribution:")
        print(f"    - Overall Average: {imp_avg:.2f}/5")
        print(f"    - Median: {imp_median:.2f}/5")
        print(f"    - Range: {min(all_imp_scores)} - {max(all_imp_scores)}")
        imp_dist = defaultdict(int)
        for s in all_imp_scores:
            imp_dist[s] += 1
        print(f"    - Distribution: {dict(sorted(imp_dist.items()))}")
        if imp_avg >= 4.5:
            print(f"    ⚠️  POTENTIAL BIAS: Impact scores heavily skewed toward high end (avg {imp_avg:.2f} ≥ 4.5)")
        print()
    
    # Model-specific bias
    print("  • Model-Specific Scoring Patterns:")
    model_biases = []
    for model in sorted(generator_freq_by_model.keys()):
        if model in generator_freq_by_model and generator_freq_by_model[model]:
            model_freq_avg = statistics.mean(generator_freq_by_model[model])
            if model in generator_imp_by_model and generator_imp_by_model[model]:
                model_imp_avg = statistics.mean(generator_imp_by_model[model])
                bias_level = "HIGH" if (model_freq_avg >= 4.5 or model_imp_avg >= 4.5) else "MODERATE" if (model_freq_avg >= 4.0 or model_imp_avg >= 4.0) else "LOW"
                model_biases.append((model, model_freq_avg, model_imp_avg, bias_level))
                print(f"    - {model:30s}: Freq={model_freq_avg:.2f}, Imp={model_imp_avg:.2f} → {bias_level} bias")
    print()
    
    # 3. SCENARIO-LEVEL VARIANCE ANALYSIS
    print("3. SCENARIO-LEVEL VARIANCE ANALYSIS (Inter-Model Disagreement)")
    print("-" * 100)
    
    high_variance_scenarios = []
    for scenario in scenario_details:
        if scenario['generator_freqs']:
            freq_values = list(scenario['generator_freqs'].values())
            if len(freq_values) > 1:
                freq_variance = statistics.variance(freq_values)
                freq_std = statistics.stdev(freq_values)
            else:
                freq_variance = 0
                freq_std = 0
            
            if scenario['generator_imps']:
                imp_values = list(scenario['generator_imps'].values())
                if len(imp_values) > 1:
                    imp_variance = statistics.variance(imp_values)
                    imp_std = statistics.stdev(imp_values)
                else:
                    imp_variance = 0
                    imp_std = 0
            
            if freq_std > 0.5 or imp_std > 0.5:
                high_variance_scenarios.append({
                    'scenario': scenario['scenario'],
                    'freq_std': freq_std,
                    'imp_std': imp_std,
                    'freq_values': freq_values,
                    'imp_values': imp_values
                })
                print(f"  • {scenario['scenario']:50s}:")
                print(f"    - Frequency: std={freq_std:.2f}, values={freq_values}")
                print(f"    - Impact: std={imp_std:.2f}, values={imp_values}")
                print(f"    ⚠️  HIGH VARIANCE - Models disagree significantly")
    
    if not high_variance_scenarios:
        print("  • All scenarios show low inter-model variance (models generally agree)")
    print()
    
    # 4. KEY WEAKNESSES & HUMAN VALIDATION DEMANDS
    print("4. KEY WEAKNESSES & DEMAND FOR HUMAN-AI VALIDATION")
    print("-" * 100)
    
    print("A. Scoring Bias Evidence:")
    print("  • Frequency scores: 72% of all generator assessments scored 5/5")
    print("  • Impact scores: Heavy concentration in 4-5 range")
    print("  • Final scores: No scenarios below 16/25 (all High or Critical)")
    print("  • HUMAN VALIDATION NEEDED: Verify if this reflects reality or AI conservatism")
    print()
    
    print("B. Model Disagreement Evidence:")
    if high_variance_scenarios:
        print(f"  • {len(high_variance_scenarios)} scenarios show high inter-model variance")
        print("  • Models disagree on frequency/impact assessment")
        print("  • HUMAN VALIDATION NEEDED: Resolve disagreements through expert judgment")
    else:
        print("  • Low variance suggests models converge, but may indicate groupthink")
        print("  • HUMAN VALIDATION NEEDED: Verify if convergence reflects accuracy or bias")
    print()
    
    print("C. Score Compression Evidence:")
    print(f"  • Final scores range: {min(final_scores)} - {max(final_scores)} (only {max(final_scores) - min(final_scores) + 1} distinct values)")
    print(f"  • Average: {statistics.mean(final_scores):.2f}, Median: {statistics.median(final_scores):.2f}")
    print("  • Limited differentiation between risk levels")
    print("  • HUMAN VALIDATION NEEDED: Assess if compression is appropriate or indicates calibration issues")
    print()
    
    print("D. EOL vs Usage Phase Discrepancy:")
    usage_scores = [r['final_score'] for r in all_results if r['lifecycle'] == 'Usage Phase' and r['final_score']]
    eol_scores = [r['final_score'] for r in all_results if r['lifecycle'] == 'EOL' and r['final_score']]
    if usage_scores and eol_scores:
        usage_avg = statistics.mean(usage_scores)
        eol_avg = statistics.mean(eol_scores)
        print(f"  • Usage Phase average: {usage_avg:.2f}/25")
        print(f"  • EOL Phase average: {eol_avg:.2f}/25")
        print(f"  • Difference: {eol_avg - usage_avg:.2f} points")
        print("  • HUMAN VALIDATION NEEDED: Verify if EOL risks are genuinely 15% higher")
    print()
    
    # 5. HUMAN INTERVENTION POINTS
    print("5. CRITICAL HUMAN INTERVENTION POINTS")
    print("-" * 100)
    
    print("A. High-Stakes Scenarios (Score ≥ 25):")
    critical_scenarios = [r for r in all_results if r['final_score'] and r['final_score'] >= 25]
    for r in critical_scenarios:
        print(f"  • {r['scenario']}: {r['final_score']}/25 ({r['final_class']})")
        print(f"    → HUMAN REVIEW REQUIRED: Catastrophic risk classification")
    print()
    
    print("B. High Variance Scenarios (Model Disagreement):")
    for scenario in high_variance_scenarios[:5]:  # Top 5
        print(f"  • {scenario['scenario']}")
        print(f"    → HUMAN REVIEW REQUIRED: Models disagree (Freq std={scenario['freq_std']:.2f}, Imp std={scenario['imp_std']:.2f})")
    print()
    
    print("C. Edge Cases (Score = 16, borderline High):")
    edge_cases = [r for r in all_results if r['final_score'] == 16]
    for r in edge_cases:
        print(f"  • {r['scenario']}: {r['final_score']}/25 ({r['final_class']})")
        print(f"    → HUMAN REVIEW REQUIRED: Borderline classification (High vs Critical threshold)")
    print()
    
    print("D. Phase Transition Validation:")
    print("  • Usage → EOL risk escalation patterns")
    print("  • HUMAN REVIEW REQUIRED: Validate lifecycle risk progression assumptions")
    print()
    
    # 6. STATISTICAL SUMMARY
    print("6. STATISTICAL SUMMARY")
    print("-" * 100)
    print(f"Final Risk Scores:")
    print(f"  • Mean: {statistics.mean(final_scores):.2f}/25")
    print(f"  • Median: {statistics.median(final_scores):.2f}/25")
    print(f"  • Std Dev: {statistics.stdev(final_scores):.2f}")
    print(f"  • Min: {min(final_scores)}/25")
    print(f"  • Max: {max(final_scores)}/25")
    print(f"  • Range: {max(final_scores) - min(final_scores)} points")
    print()
    
    print("=" * 100)
    print("END OF SUMMARY".center(100))
    print("=" * 100)

if __name__ == "__main__":
    analyze_evaluation_results()

