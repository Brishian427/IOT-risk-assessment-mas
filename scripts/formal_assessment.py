"""
Formal Assessment Script
Run batch evaluation and save results to a dedicated formal assessment directory
Created: 2025-12-09
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import run_risk_assessment
from tqdm import tqdm


def load_input_file(filepath: Path) -> str:
    """Load risk input from a text file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def formal_assessment(
    inputs_dir: str = "evaluation_inputs",
    pattern: str = "scenario_*.txt",
    enable_logging: bool = True
) -> List[dict]:
    """
    Run formal assessment and save to dedicated directory
    
    Args:
        inputs_dir: Directory containing input files
        pattern: File pattern to match (default: "scenario_*.txt")
        enable_logging: Whether to enable logging
        
    Returns:
        List of results for each input
    """
    # Create formal assessment directory
    timestamp = datetime.now().strftime("%Y%m%d")
    formal_dir = Path("results") / f"formal_assessment_{timestamp}"
    formal_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("🎯 FORMAL ASSESSMENT - Dual-Factor Risk Assessment")
    print("=" * 80)
    print(f"📁 Output Directory: {formal_dir}")
    print()
    
    inputs_path = Path(inputs_dir)
    
    if not inputs_path.exists():
        print(f"❌ Directory not found: {inputs_dir}")
        return []
    
    # Find all matching files
    input_files = sorted(inputs_path.glob(pattern))
    
    if not input_files:
        print(f"⚠️  No files found matching pattern: {pattern}")
        return []
    
    print(f"📋 Found {len(input_files)} scenario file(s):")
    for f in input_files:
        print(f"   - {f.name}")
    print()
    
    results = []
    
    # Process each file
    for idx, input_file in enumerate(tqdm(input_files, desc="Processing Scenarios", unit="scenario"), 1):
        try:
            # Load input
            risk_input = load_input_file(input_file)
            
            print(f"\n{'='*80}")
            print(f"📄 [{idx}/{len(input_files)}] Processing: {input_file.name}")
            print(f"{'='*80}")
            
            # Run assessment with custom output directory
            result = run_risk_assessment(
                risk_input=risk_input,
                save_result=True,
                enable_logging=enable_logging,
                output_dir=str(formal_dir)
            )
            
            # Store result with metadata
            results.append({
                "file": input_file.name,
                "input": risk_input,
                "result": result
            })
            
            # Print summary
            if result.get("synthesized_draft"):
                draft = result["synthesized_draft"]
                print(f"\n✅ Assessment Complete")
                print(f"   Legacy Score: {draft.score}/5")
                
                if draft.risk_assessment:
                    ra = draft.risk_assessment
                    print(f"   Frequency: {ra.frequency_score}/5")
                    print(f"   Impact: {ra.impact_score}/5")
                    print(f"   Final Risk Score: {ra.final_risk_score}/25 ({ra.risk_classification})")
                
                print(f"   Revisions: {result.get('revision_count', 0)}")
                print(f"   Critiques: {len(result.get('critiques', []))}")
            else:
                print(f"\n⚠️  No synthesized draft generated")
                
        except Exception as e:
            print(f"\n❌ Error processing {input_file.name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                "file": input_file.name,
                "input": None,
                "result": None,
                "error": str(e)
            })
    
    # Print final summary
    print(f"\n{'='*80}")
    print(f"📊 FORMAL ASSESSMENT SUMMARY")
    print(f"{'='*80}")
    print(f"Total scenarios processed: {len(input_files)}")
    print(f"Successful: {sum(1 for r in results if r.get('result'))}")
    print(f"Failed: {sum(1 for r in results if r.get('error'))}")
    print(f"\n📁 All results saved to: {formal_dir}")
    print(f"{'='*80}\n")
    
    return results


if __name__ == "__main__":
    formal_assessment()

