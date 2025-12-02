"""
Main Entry Point for Multi-Agent System
Created: 2025-01-XX
"""

from typing import Dict, Any
from tqdm import tqdm
from src.graph import workflow
from src.schemas import StateSchema
from src.config import Config


def run_risk_assessment(risk_input: str) -> Dict[str, Any]:
    """
    Run the complete risk assessment workflow
    
    Args:
        risk_input: Description of the IoT device scenario
        
    Returns:
        Final state with synthesized_draft and critiques
    """
    # Validate API keys
    missing_keys = Config.validate_api_keys()
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    # Initialize state
    initial_state: StateSchema = {
        "risk_input": risk_input,
        "draft_assessments": [],
        "synthesized_draft": None,
        "critiques": [],
        "revision_count": 0
    }
    
    # Run workflow with progress tracking
    print("\n🔄 Running Multi-Agent Workflow...\n")
    final_state = workflow.invoke(initial_state)
    print()  # New line after progress bars
    
    return final_state


def run_risk_assessment_async(risk_input: str):
    """
    Run the complete risk assessment workflow asynchronously
    
    Args:
        risk_input: Description of the IoT device scenario
        
    Returns:
        Async generator yielding state updates
    """
    # Validate API keys
    missing_keys = Config.validate_api_keys()
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    # Initialize state
    initial_state: StateSchema = {
        "risk_input": risk_input,
        "draft_assessments": [],
        "synthesized_draft": None,
        "critiques": [],
        "revision_count": 0
    }
    
    # Stream workflow execution
    for state in workflow.stream(initial_state):
        yield state


if __name__ == "__main__":
    # Example usage
    example_input = """
    IoT Smart Thermostat Device:
    - Connects to home WiFi network
    - No encryption on firmware updates
    - Default admin password (admin/admin)
    - Collects user temperature preferences
    - No security update mechanism
    - PSTI Act 2022 compliance status unknown
    """
    
    print("Running risk assessment...")
    result = run_risk_assessment(example_input)
    
    print("\n=== Final Assessment ===")
    if result.get("synthesized_draft"):
        draft = result["synthesized_draft"]
        print(f"Score: {draft.score}/5")
        print(f"Summary: {draft.reasoning.summary}")
        print(f"\nKey Arguments:")
        for arg in draft.reasoning.key_arguments:
            print(f"  - {arg}")
        print(f"\nRegulatory Citations: {', '.join(draft.reasoning.regulatory_citations)}")
        print(f"Vulnerabilities: {', '.join(draft.reasoning.vulnerabilities)}")
    
    print(f"\n=== Critiques ({len(result.get('critiques', []))}) ===")
    for critique in result.get("critiques", []):
        print(f"\n{critique.challenger_name}:")
        print(f"  Valid: {critique.is_valid}")
        print(f"  Confidence: {critique.confidence:.2%}")
        print(f"  Recommendation: {critique.recommendation}")
        if critique.issues:
            print(f"  Issues: {', '.join(critique.issues)}")
    
    print(f"\nRevision Count: {result.get('revision_count', 0)}")

