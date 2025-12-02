"""
Individual Agent Tests
Created: 2025-01-XX
"""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.schemas import RiskAssessment, ReasoningTrace, StateSchema
from src.agents.generator_ensemble import generator_ensemble_node
from src.agents.aggregator import aggregator_node
from src.agents.challenger_a import challenger_a_node
from src.agents.challenger_b import challenger_b_node
from src.agents.challenger_c import challenger_c_node


def test_generator_ensemble():
    """Test Generator Ensemble node"""
    print("\n[TEST] Generator Ensemble")
    print("-" * 60)
    
    state: StateSchema = {
        "risk_input": "IoT device with no security features",
        "draft_assessments": [],
        "synthesized_draft": None,
        "critiques": [],
        "revision_count": 0
    }
    
    try:
        import asyncio
        result = asyncio.run(generator_ensemble_node(state))
        print(f"✓ Generated {len(result['draft_assessments'])} assessments")
        for assess in result['draft_assessments'][:3]:  # Show first 3
            print(f"  - {assess.model_name}: Score {assess.score}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_aggregator():
    """Test Aggregator node"""
    print("\n[TEST] Aggregator")
    print("-" * 60)
    
    # Create mock assessments
    mock_assessments = [
        RiskAssessment(
            model_name="test_model_1",
            score=4,
            reasoning=ReasoningTrace(
                summary="High risk device",
                key_arguments=["No encryption", "Default passwords"],
                regulatory_citations=["PSTI Act 2022"],
                vulnerabilities=["CVE-2024-12345"]
            )
        ),
        RiskAssessment(
            model_name="test_model_2",
            score=3,
            reasoning=ReasoningTrace(
                summary="Medium risk device",
                key_arguments=["Weak authentication"],
                regulatory_citations=[],
                vulnerabilities=[]
            )
        )
    ]
    
    state: StateSchema = {
        "risk_input": "Test device",
        "draft_assessments": mock_assessments,
        "synthesized_draft": None,
        "critiques": [],
        "revision_count": 0
    }
    
    try:
        result = aggregator_node(state)
        if result.get("synthesized_draft"):
            draft = result["synthesized_draft"]
            print(f"✓ Synthesized draft: Score {draft.score}")
            print(f"  Summary: {draft.reasoning.summary[:50]}...")
            return True
        else:
            print("✗ No synthesized draft created")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_challenger_a():
    """Test Challenger A (Logic) node"""
    print("\n[TEST] Challenger A (Logic)")
    print("-" * 60)
    
    state: StateSchema = {
        "risk_input": "Test device",
        "draft_assessments": [],
        "synthesized_draft": RiskAssessment(
            model_name="test",
            score=5,
            reasoning=ReasoningTrace(
                summary="Critical risk",
                key_arguments=["Minor issue"],
                regulatory_citations=[],
                vulnerabilities=[]
            )
        ),
        "critiques": [],
        "revision_count": 0
    }
    
    try:
        result = challenger_a_node(state)
        critique = result["critiques"][0] if result.get("critiques") else None
        if critique:
            print(f"✓ Critique generated: {critique.challenger_name}")
            print(f"  Valid: {critique.is_valid}, Recommendation: {critique.recommendation}")
            return True
        else:
            print("✗ No critique generated")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_challenger_b():
    """Test Challenger B (Source) node"""
    print("\n[TEST] Challenger B (Source)")
    print("-" * 60)
    
    state: StateSchema = {
        "risk_input": "Test device",
        "draft_assessments": [],
        "synthesized_draft": RiskAssessment(
            model_name="test",
            score=4,
            reasoning=ReasoningTrace(
                summary="High risk with CVE",
                key_arguments=["Unpatched vulnerability"],
                regulatory_citations=["PSTI Act 2022"],
                vulnerabilities=["CVE-2024-12345"]
            )
        ),
        "critiques": [],
        "revision_count": 0
    }
    
    try:
        result = challenger_b_node(state)
        critique = result["critiques"][0] if result.get("critiques") else None
        if critique:
            print(f"✓ Critique generated: {critique.challenger_name}")
            print(f"  Valid: {critique.is_valid}, Issues: {len(critique.issues)}")
            return True
        else:
            print("✗ No critique generated")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_challenger_c():
    """Test Challenger C (Safety) node"""
    print("\n[TEST] Challenger C (Safety)")
    print("-" * 60)
    
    state: StateSchema = {
        "risk_input": "Test device",
        "draft_assessments": [],
        "synthesized_draft": RiskAssessment(
            model_name="test",
            score=3,
            reasoning=ReasoningTrace(
                summary="Compliance check needed",
                key_arguments=["Missing ISO certification"],
                regulatory_citations=["ISO 27001"],
                vulnerabilities=[]
            )
        ),
        "critiques": [],
        "revision_count": 0
    }
    
    try:
        result = challenger_c_node(state)
        critique = result["critiques"][0] if result.get("critiques") else None
        if critique:
            print(f"✓ Critique generated: {critique.challenger_name}")
            print(f"  Valid: {critique.is_valid}, Recommendation: {critique.recommendation}")
            return True
        else:
            print("✗ No critique generated")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_all_tests():
    """Run all individual agent tests"""
    print("=" * 60)
    print("INDIVIDUAL AGENT TESTS")
    print("=" * 60)
    
    results = {
        "Generator Ensemble": test_generator_ensemble(),
        "Aggregator": test_aggregator(),
        "Challenger A": test_challenger_a(),
        "Challenger B": test_challenger_b(),
        "Challenger C": test_challenger_c(),
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    return all_passed


if __name__ == "__main__":
    run_all_tests()

