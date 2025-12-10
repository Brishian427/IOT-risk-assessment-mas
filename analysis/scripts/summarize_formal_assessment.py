"""
Summarize Formal Assessment Results
Created: 2025-12-09
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

def load_assessment(filepath: Path) -> Dict:
    """Load assessment JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_scenario_name(risk_input: str) -> str:
    """Extract scenario name from risk input"""
    lines = risk_input.split('\n')
    for line in lines:
        if 'Risk Category:' in line:
            return line.split('Risk Category:')[1].strip()
    return "Unknown"

def summarize_formal_assessment():
    """Summarize all formal assessment results"""
    formal_dir = Path('results/formal_assessment_20251210')
    
    if not formal_dir.exists():
        print(f"❌ Directory not found: {formal_dir}")
        return
    
    # Find all JSON files
    json_files = sorted(formal_dir.glob('*.json'))
    
    if not json_files:
        print(f"⚠️  No JSON files found in {formal_dir}")
        return
    
    print("=" * 80)
    print("📊 FORMAL ASSESSMENT RESULTS SUMMARY")
    print("=" * 80)
    print(f"\n📁 Directory: {formal_dir}")
    print(f"📄 Total Assessments: {len(json_files)}\n")
    
    results = []
    usage_phase = []
    eol_phase = []
    
    for filepath in json_files:
        try:
            data = load_assessment(filepath)
            draft = data['output']['synthesized_draft']
            
            # Extract scenario info
            risk_input = data['metadata']['risk_input']
            scenario_name = extract_scenario_name(risk_input)
            
            # Extract lifecycle stage
            lifecycle = "Unknown"
            if "Usage Phase" in risk_input:
                lifecycle = "Usage Phase"
            elif "End-of-Life" in risk_input or "EOL" in risk_input:
                lifecycle = "End-of-Life (EOL)"
            
            # Extract scores
            legacy_score = draft['score']
            
            if 'risk_assessment' in draft:
                ra = draft['risk_assessment']
                frequency = ra['frequency_score']
                impact = ra['impact_score']
                final_score = ra['final_risk_score']
                classification = ra['risk_classification']
            else:
                frequency = None
                impact = None
                final_score = None
                classification = None
            
            revision_count = data['metadata']['revision_count']
            total_critiques = data['metadata']['total_critiques']
            
            result = {
                'file': filepath.name,
                'scenario': scenario_name,
                'lifecycle': lifecycle,
                'legacy_score': legacy_score,
                'frequency': frequency,
                'impact': impact,
                'final_score': final_score,
                'classification': classification,
                'revisions': revision_count,
                'critiques': total_critiques
            }
            
            results.append(result)
            
            if lifecycle == "Usage Phase":
                usage_phase.append(result)
            elif lifecycle == "End-of-Life (EOL)":
                eol_phase.append(result)
                
        except Exception as e:
            print(f"⚠️  Error processing {filepath.name}: {str(e)}")
    
    # Print detailed results
    print("=" * 80)
    print("📋 DETAILED RESULTS BY SCENARIO")
    print("=" * 80)
    
    for idx, result in enumerate(results, 1):
        print(f"\n[{idx}] {result['scenario']}")
        print(f"    Lifecycle: {result['lifecycle']}")
        print(f"    Legacy Score: {result['legacy_score']}/5")
        if result['frequency'] is not None:
            print(f"    Frequency: {result['frequency']}/5")
            print(f"    Impact: {result['impact']}/5")
            print(f"    Final Risk Score: {result['final_score']}/25 ({result['classification']})")
            print(f"    Calculation: {result['frequency']} × {result['impact']} = {result['final_score']}")
        print(f"    Revisions: {result['revisions']}")
        print(f"    Critiques: {result['critiques']}")
    
    # Print summary statistics
    print(f"\n{'=' * 80}")
    print("📊 SUMMARY STATISTICS")
    print("=" * 80)
    
    # Overall statistics
    if results:
        legacy_scores = [r['legacy_score'] for r in results]
        final_scores = [r['final_score'] for r in results if r['final_score'] is not None]
        frequencies = [r['frequency'] for r in results if r['frequency'] is not None]
        impacts = [r['impact'] for r in results if r['impact'] is not None]
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Scenarios: {len(results)}")
        print(f"   Usage Phase: {len(usage_phase)}")
        print(f"   End-of-Life: {len(eol_phase)}")
        
        if legacy_scores:
            print(f"\n   Legacy Scores (1-5):")
            print(f"     Average: {sum(legacy_scores) / len(legacy_scores):.2f}")
            print(f"     Min: {min(legacy_scores)}")
            print(f"     Max: {max(legacy_scores)}")
        
        if final_scores:
            print(f"\n   Final Risk Scores (1-25):")
            print(f"     Average: {sum(final_scores) / len(final_scores):.2f}")
            print(f"     Min: {min(final_scores)}")
            print(f"     Max: {max(final_scores)}")
        
        if frequencies:
            print(f"\n   Frequency Scores (1-5):")
            print(f"     Average: {sum(frequencies) / len(frequencies):.2f}")
            print(f"     Min: {min(frequencies)}")
            print(f"     Max: {max(frequencies)}")
        
        if impacts:
            print(f"\n   Impact Scores (1-5):")
            print(f"     Average: {sum(impacts) / len(impacts):.2f}")
            print(f"     Min: {min(impacts)}")
            print(f"     Max: {max(impacts)}")
        
        # Classification distribution
        classifications = defaultdict(int)
        for r in results:
            if r['classification']:
                classifications[r['classification']] += 1
        
        if classifications:
            print(f"\n   Risk Classification Distribution:")
            for cls, count in sorted(classifications.items(), key=lambda x: x[1], reverse=True):
                print(f"     {cls}: {count}")
    
    # Usage Phase statistics
    if usage_phase:
        print(f"\n📊 Usage Phase Statistics ({len(usage_phase)} scenarios):")
        usage_final = [r['final_score'] for r in usage_phase if r['final_score'] is not None]
        usage_freq = [r['frequency'] for r in usage_phase if r['frequency'] is not None]
        usage_impact = [r['impact'] for r in usage_phase if r['impact'] is not None]
        
        if usage_final:
            print(f"   Average Final Score: {sum(usage_final) / len(usage_final):.2f}/25")
        if usage_freq:
            print(f"   Average Frequency: {sum(usage_freq) / len(usage_freq):.2f}/5")
        if usage_impact:
            print(f"   Average Impact: {sum(usage_impact) / len(usage_impact):.2f}/5")
    
    # EOL Phase statistics
    if eol_phase:
        print(f"\n📊 End-of-Life Phase Statistics ({len(eol_phase)} scenarios):")
        eol_final = [r['final_score'] for r in eol_phase if r['final_score'] is not None]
        eol_freq = [r['frequency'] for r in eol_phase if r['frequency'] is not None]
        eol_impact = [r['impact'] for r in eol_phase if r['impact'] is not None]
        
        if eol_final:
            print(f"   Average Final Score: {sum(eol_final) / len(eol_final):.2f}/25")
        if eol_freq:
            print(f"   Average Frequency: {sum(eol_freq) / len(eol_freq):.2f}/5")
        if eol_impact:
            print(f"   Average Impact: {sum(eol_impact) / len(eol_impact):.2f}/5")
    
    # Workflow statistics
    print(f"\n🔄 Workflow Statistics:")
    revisions = [r['revisions'] for r in results]
    critiques = [r['critiques'] for r in results]
    
    if revisions:
        print(f"   Average Revisions: {sum(revisions) / len(revisions):.2f}")
        print(f"   Min Revisions: {min(revisions)}")
        print(f"   Max Revisions: {max(revisions)}")
    
    if critiques:
        print(f"   Average Critiques: {sum(critiques) / len(critiques):.2f}")
        print(f"   Min Critiques: {min(critiques)}")
        print(f"   Max Critiques: {max(critiques)}")
    
    # Table format
    print(f"\n{'=' * 80}")
    print("📋 RESULTS TABLE")
    print("=" * 80)
    print(f"{'Scenario':<40} {'Lifecycle':<15} {'Freq':<5} {'Imp':<5} {'Final':<6} {'Class':<10}")
    print("-" * 80)
    
    for result in results:
        scenario = result['scenario'][:38]
        lifecycle = result['lifecycle'][:13]
        freq = str(result['frequency']) if result['frequency'] else 'N/A'
        imp = str(result['impact']) if result['impact'] else 'N/A'
        final = str(result['final_score']) if result['final_score'] else 'N/A'
        cls = result['classification'] or 'N/A'
        
        print(f"{scenario:<40} {lifecycle:<15} {freq:<5} {imp:<5} {final:<6} {cls:<10}")
    
    print("=" * 80)
    print(f"\n✅ Summary complete! All results saved in: {formal_dir}\n")

if __name__ == "__main__":
    summarize_formal_assessment()

