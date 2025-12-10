"""
Batch Evaluation Script
Process multiple evaluation inputs from evaluation_inputs/ directory
Created: 2025-12-09
"""

import sys
import os
from pathlib import Path
from typing import List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import run_risk_assessment
from tqdm import tqdm


def load_input_file(filepath: Path) -> str:
    """Load risk input from a text file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def batch_evaluate(
    inputs_dir: str = "evaluation_inputs",
    pattern: str = "*.txt",
    save_results: bool = True,
    enable_logging: bool = True
) -> List[dict]:
    """
    Batch process all evaluation inputs
    
    Args:
        inputs_dir: Directory containing input files
        pattern: File pattern to match (default: "*.txt")
        save_results: Whether to save individual results
        enable_logging: Whether to enable logging
        
    Returns:
        List of results for each input
    """
    inputs_path = Path(inputs_dir)
    
    if not inputs_path.exists():
        print(f"❌ Directory not found: {inputs_dir}")
        return []
    
    # Find all matching files
    input_files = sorted(inputs_path.glob(pattern))
    
    if not input_files:
        print(f"⚠️  No files found matching pattern: {pattern}")
        return []
    
    print(f"📁 Found {len(input_files)} input file(s)\n")
    
    results = []
    
    # Process each file
    for input_file in tqdm(input_files, desc="Processing", unit="file"):
        try:
            # Load input
            risk_input = load_input_file(input_file)
            
            print(f"\n{'='*60}")
            print(f"📄 Processing: {input_file.name}")
            print(f"{'='*60}")
            
            # Run assessment
            result = run_risk_assessment(
                risk_input=risk_input,
                save_result=save_results,
                enable_logging=enable_logging
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
                print(f"   Score: {draft.score}/5")
                print(f"   Revisions: {result.get('revision_count', 0)}")
                print(f"   Critiques: {len(result.get('critiques', []))}")
            else:
                print(f"\n⚠️  No synthesized draft generated")
                
        except Exception as e:
            print(f"\n❌ Error processing {input_file.name}: {str(e)}")
            results.append({
                "file": input_file.name,
                "input": None,
                "result": None,
                "error": str(e)
            })
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 Batch Evaluation Summary")
    print(f"{'='*60}")
    print(f"Total files processed: {len(input_files)}")
    print(f"Successful: {sum(1 for r in results if r.get('result'))}")
    print(f"Failed: {sum(1 for r in results if r.get('error'))}")
    
    return results


def evaluate_single(
    filename: str,
    inputs_dir: str = "evaluation_inputs"
) -> Optional[dict]:
    """
    Evaluate a single input file
    
    Args:
        filename: Name of the input file
        inputs_dir: Directory containing input files
        
    Returns:
        Result dictionary or None if file not found
    """
    inputs_path = Path(inputs_dir)
    input_file = inputs_path / filename
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        return None
    
    risk_input = load_input_file(input_file)
    
    print(f"📄 Evaluating: {filename}\n")
    
    result = run_risk_assessment(
        risk_input=risk_input,
        save_result=True,
        enable_logging=True
    )
    
    return {
        "file": filename,
        "input": risk_input,
        "result": result
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch evaluate IoT risk assessment inputs")
    parser.add_argument(
        "--file",
        type=str,
        help="Evaluate a single file (e.g., example_1_smart_thermostat.txt)"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="evaluation_inputs",
        help="Directory containing input files (default: evaluation_inputs)"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.txt",
        help="File pattern to match (default: *.txt)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save individual results"
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Disable logging"
    )
    
    args = parser.parse_args()
    
    if args.file:
        # Single file mode
        evaluate_single(args.file, args.dir)
    else:
        # Batch mode
        batch_evaluate(
            inputs_dir=args.dir,
            pattern=args.pattern,
            save_results=not args.no_save,
            enable_logging=not args.no_log
        )

