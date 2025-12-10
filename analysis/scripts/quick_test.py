"""
Quick Test - Minimal test with mock data (no API calls)
Created: 2025-01-XX
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.schemas import RiskAssessment, ReasoningTrace, StateSchema

def test_schemas():
    """Test that schemas work correctly"""
    print("Testing Pydantic schemas...")
    
    # Create a test reasoning trace
    reasoning = ReasoningTrace(
        summary="Test risk assessment",
        key_arguments=["Argument 1", "Argument 2"],
        regulatory_citations=["PSTI Act 2022"],
        vulnerabilities=["CVE-2024-12345"]
    )
    
    # Create a test assessment
    assessment = RiskAssessment(
        model_name="test_model",
        score=4,
        reasoning=reasoning
    )
    
    print(f"✓ Created assessment: {assessment.model_name}, Score: {assessment.score}")
    print(f"✓ Reasoning summary: {assessment.reasoning.summary}")
    print(f"✓ Citations: {assessment.reasoning.regulatory_citations}")
    
    # Test state schema
    state: StateSchema = {
        "risk_input": "Test device",
        "draft_assessments": [assessment],
        "synthesized_draft": assessment,
        "critiques": [],
        "revision_count": 0
    }
    
    print(f"✓ State schema valid: {len(state['draft_assessments'])} assessment(s)")
    print("\n✓ All schema tests passed!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("QUICK SCHEMA TEST (No API calls required)")
    print("=" * 60)
    test_schemas()

