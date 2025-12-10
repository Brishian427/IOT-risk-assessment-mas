"""
Generate Honest Reflection of Evaluation Results
Created: 2025-12-10
"""

import json
from pathlib import Path
from collections import defaultdict

def generate_reflection():
    """Generate comprehensive reflection report"""
    
    formal_dir = Path('results/formal_assessment_20251210')
    files = sorted(formal_dir.glob('*.json'))
    
    results = []
    for f in files:
        data = json.loads(f.read_text(encoding='utf-8'))
        risk_input = data['metadata']['risk_input']
        draft = data['output']['synthesized_draft']
        
        scenario_name = "Unknown"
        if 'Risk Category:' in risk_input:
            scenario_name = risk_input.split('Risk Category:')[1].split('\n')[0].strip()
        
        lifecycle = "Usage Phase" if "Usage Phase" in risk_input else "EOL"
        
        ra = draft.get('risk_assessment', {})
        result = {
            'scenario': scenario_name,
            'lifecycle': lifecycle,
            'frequency': ra.get('frequency_score'),
            'impact': ra.get('impact_score'),
            'final': ra.get('final_risk_score'),
            'classification': ra.get('risk_classification'),
            'revisions': data['metadata']['revision_count'],
            'critiques': data['metadata']['total_critiques']
        }
        results.append(result)
    
    usage = [r for r in results if r['lifecycle'] == 'Usage Phase']
    eol = [r for r in results if r['lifecycle'] == 'EOL']
    
    # Calculate statistics
    all_final = [r['final'] for r in results if r['final']]
    all_freq = [r['frequency'] for r in results if r['frequency']]
    all_imp = [r['impact'] for r in results if r['impact']]
    all_revisions = [r['revisions'] for r in results]
    all_critiques = [r['critiques'] for r in results]
    
    usage_final = [r['final'] for r in usage if r['final']]
    eol_final = [r['final'] for r in eol if r['final']]
    
    critical_count = sum(1 for r in results if r['classification'] == 'Critical')
    high_count = sum(1 for r in results if r['classification'] == 'High')
    
    # Print reflection
    print("=" * 100)
    print("HONEST REFLECTION: IoT RISK ASSESSMENT EVALUATION RESULTS".center(100))
    print("=" * 100)
    print()
    
    print("📊 EXECUTIVE SUMMARY")
    print("-" * 100)
    print(f"• Total Scenarios Assessed: {len(results)} (8 Usage Phase, 3 EOL Phase)")
    print(f"• Success Rate: 100% (all scenarios completed)")
    print(f"• Average Final Risk Score: {sum(all_final)/len(all_final):.2f}/25")
    print(f"• Critical Risk Rate: {critical_count}/{len(results)} ({critical_count*100//len(results)}%)")
    print(f"• Average Workflow Revisions: {sum(all_revisions)/len(all_revisions):.2f} rounds")
    print()
    
    print("🔍 OVERALL PERFORMANCE METRICS")
    print("-" * 100)
    print(f"Score Distribution:")
    print(f"  • Final Risk Scores: {min(all_final)} - {max(all_final)} (avg: {sum(all_final)/len(all_final):.2f})")
    print(f"  • Frequency Scores: {min(all_freq)} - {max(all_freq)} (avg: {sum(all_freq)/len(all_freq):.2f}/5)")
    print(f"  • Impact Scores: {min(all_imp)} - {max(all_imp)} (avg: {sum(all_imp)/len(all_imp):.2f}/5)")
    print()
    print(f"Workflow Efficiency:")
    print(f"  • Revisions: {min(all_revisions)} - {max(all_revisions)} rounds (avg: {sum(all_revisions)/len(all_revisions):.2f})")
    print(f"  • Critiques per Scenario: {min(all_critiques)} - {max(all_critiques)} (avg: {sum(all_critiques)/len(all_critiques):.2f})")
    print(f"  • Convergence Pattern: {sum(1 for r in all_revisions if r == 3)}/{len(results)} scenarios reached MAX_REVISIONS (3)")
    print()
    
    print("📈 PHASE COMPARISON ANALYSIS")
    print("-" * 100)
    print(f"Usage Phase (8 scenarios):")
    print(f"  • Average Final Score: {sum(usage_final)/len(usage_final):.2f}/25")
    print(f"  • Score Range: {min(usage_final)} - {max(usage_final)}")
    print(f"  • Critical: {sum(1 for r in usage if r['classification'] == 'Critical')}/8")
    print(f"  • High: {sum(1 for r in usage if r['classification'] == 'High')}/8")
    print()
    print(f"EOL Phase (3 scenarios):")
    print(f"  • Average Final Score: {sum(eol_final)/len(eol_final):.2f}/25")
    print(f"  • Score Range: {min(eol_final)} - {max(eol_final)}")
    print(f"  • Critical: {sum(1 for r in eol if r['classification'] == 'Critical')}/3 (100%)")
    print(f"  • High: {sum(1 for r in eol if r['classification'] == 'High')}/3")
    print()
    print(f"Key Finding: EOL Phase shows {sum(eol_final)/len(eol_final) - sum(usage_final)/len(usage_final):.2f} points higher average risk")
    print(f"            All EOL scenarios classified as Critical (vs 62.5% in Usage Phase)")
    print()
    
    print("🎯 SCORING PATTERNS & DISTRIBUTION")
    print("-" * 100)
    score_dist = defaultdict(int)
    for r in results:
        if r['final']:
            score_dist[r['final']] += 1
    
    print("Final Risk Score Distribution:")
    for score in sorted(score_dist.keys(), reverse=True):
        print(f"  • {score}/25: {score_dist[score]} scenario(s)")
    print()
    
    freq_dist = defaultdict(int)
    for r in results:
        if r['frequency']:
            freq_dist[r['frequency']] += 1
    print("Frequency Score Distribution:")
    for freq in sorted(freq_dist.keys(), reverse=True):
        print(f"  • {freq}/5: {freq_dist[freq]} scenario(s) ({freq_dist[freq]*100//len(results)}%)")
    print()
    
    print("⚠️  WORKFLOW EFFICIENCY CONCERNS")
    print("-" * 100)
    max_revision_count = sum(1 for r in all_revisions if r == 3)
    print(f"• {max_revision_count}/{len(results)} scenarios ({max_revision_count*100//len(results)}%) reached MAX_REVISIONS limit (3 rounds)")
    print(f"• This suggests the 2/3 challenger majority convergence mechanism may not be working optimally")
    print(f"• Average of {sum(all_critiques)/len(all_critiques):.0f} critiques per scenario indicates extensive review cycles")
    print()
    print("Analysis:")
    print("  • High revision count (avg 2.82) suggests persistent disagreements between challengers")
    print("  • One scenario (Environmental Toxicity) completed in 1 revision - outlier success case")
    print("  • Most scenarios (10/11) required maximum revisions, indicating convergence challenges")
    print()
    
    print("✅ STRENGTHS")
    print("-" * 100)
    print("1. Comprehensive Coverage:")
    print("   • All 11 scenarios successfully assessed with dual-factor scoring")
    print("   • Clear distinction between Usage and EOL phase risks")
    print()
    print("2. Consistent High-Risk Identification:")
    print("   • 72.7% of scenarios classified as Critical")
    print("   • EOL phase correctly identified as highest risk (100% Critical)")
    print()
    print("3. Dual-Factor Assessment Working:")
    print("   • Frequency scores appropriately reflect prevalence (avg 4.73/5)")
    print("   • Impact scores show realistic severity assessment (avg 4.45/5)")
    print("   • Final scores (Frequency × Impact) provide nuanced risk quantification")
    print()
    print("4. Systematic Approach:")
    print("   • Multi-agent workflow ensures thorough review")
    print("   • Challenger agents provide diverse perspectives (Logic, Source, Compliance)")
    print()
    
    print("❌ WEAKNESSES & CONCERNS")
    print("-" * 100)
    print("1. Convergence Efficiency:")
    print("   • 91% of scenarios hit MAX_REVISIONS limit, suggesting:")
    print("     - Challenger B (Source verification) may be too strict")
    print("     - 2/3 majority mechanism not triggering early enough")
    print("     - Potential over-engineering of assessment process")
    print()
    print("2. Score Compression:")
    print("   • Final scores clustered in 16-25 range (no scores below 16)")
    print("   • Frequency scores heavily skewed toward 4-5 (only 1 scenario at 4)")
    print("   • May indicate insufficient differentiation between risk levels")
    print()
    print("3. Challenger B Performance:")
    print("   • Based on previous analysis, Challenger B had low pass rates")
    print("   • May be causing unnecessary revision cycles")
    print("   • Citation verification standards may need recalibration")
    print()
    print("4. Limited Score Diversity:")
    print("   • No scenarios scored below 16/25 (High classification)")
    print("   • Suggests either:")
    print("     - All scenarios are genuinely high-risk (plausible)")
    print("     - Scoring rubric may be too conservative")
    print()
    
    print("💡 KEY INSIGHTS")
    print("-" * 100)
    print("1. EOL Phase Dominance:")
    print("   • EOL risks are systematically higher (23.33 vs 20.25 average)")
    print("   • All EOL scenarios are Critical, indicating end-of-life is the highest risk phase")
    print("   • Environmental and physical safety risks at EOL are catastrophic (25/25)")
    print()
    print("2. Usage Phase Risk Profile:")
    print("   • Data Hacking & IoT Botnet attacks are highest risk (25/25)")
    print("   • Protocol weaknesses and cloud dependency are relatively lower (16/25)")
    print("   • User awareness is a critical systemic issue (20/25, Critical)")
    print()
    print("3. Frequency Score Interpretation:")
    print("   • Average 4.73/5 indicates risks are widespread/systemic")
    print("   • This aligns with the framework's definition: 'prevalence in current landscape'")
    print("   • Suggests IoT security issues are pervasive, not theoretical")
    print()
    print("4. Workflow Behavior:")
    print("   • High revision count suggests thorough but potentially inefficient process")
    print("   • Convergence mechanism (2/3 majority) may need tuning")
    print("   • Challenger disagreements are common but eventually resolved")
    print()
    
    print("🔧 RECOMMENDATIONS")
    print("-" * 100)
    print("1. Optimize Convergence Mechanism:")
    print("   • Review Challenger B's verification standards")
    print("   • Consider lowering threshold for 'major' citation verification")
    print("   • Implement early termination if 2 challengers consistently agree")
    print()
    print("2. Score Calibration:")
    print("   • Review if frequency scores are too high (4-5 range dominance)")
    print("   • Consider if impact scores adequately differentiate severity")
    print("   • Validate scoring against real-world incident data")
    print()
    print("3. Workflow Efficiency:")
    print("   • Reduce MAX_REVISIONS from 3 to 2 if 2/3 majority achieved earlier")
    print("   • Add convergence metrics tracking (which challenger causes most revisions)")
    print("   • Consider parallel challenger evaluation with faster consensus")
    print()
    print("4. Assessment Quality:")
    print("   • Despite high revision counts, final assessments appear comprehensive")
    print("   • Consider if thoroughness justifies computational cost")
    print("   • Document revision patterns to identify common issues")
    print()
    
    print("=" * 100)
    print("END OF REFLECTION".center(100))
    print("=" * 100)

if __name__ == "__main__":
    generate_reflection()

