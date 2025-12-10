"""
Result Saver - Auto-save assessment results to JSON files
Created: 2025-01-XX
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


def ensure_results_directory(output_dir: Optional[str] = None) -> Path:
    """Ensure results directory exists"""
    if output_dir:
        results_dir = Path(output_dir)
    else:
        results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def save_result_to_json(
    result: Dict[str, Any],
    risk_input: str,
    conversation_log: Optional[List[Dict[str, Any]]] = None,
    output_dir: Optional[str] = None
) -> str:
    """
    Save assessment result to JSON file with timestamp
    
    Args:
        result: Final state from workflow
        risk_input: Original risk input scenario
        
    Returns:
        Path to saved JSON file
    """
    # Ensure results directory exists
    results_dir = ensure_results_directory(output_dir)
    
    # Generate timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"assessment_iot_risk_{timestamp}.json"
    filepath = results_dir / filename
    
    # Prepare serializable result data
    result_data = {
        "metadata": {
            "assessment_type": "Assessment for IoT Risk",
            "timestamp": datetime.now().isoformat(),
            "risk_input": risk_input,
            "revision_count": result.get("revision_count", 0),
            "total_assessments": len(result.get("draft_assessments", [])),
            "total_critiques": len(result.get("critiques", [])),
        },
        "input": {
            "risk_scenario": risk_input
        },
        "output": {
            "synthesized_draft": None,
            "draft_assessments": [],
            "critiques": []
        },
        "workflow_stats": {
            "revision_count": result.get("revision_count", 0),
            "total_assessments_generated": len(result.get("draft_assessments", [])),
            "total_critiques": len(result.get("critiques", []))
        },
        "conversation_log": []
    }
    
    # Serialize synthesized draft
    if result.get("synthesized_draft"):
        draft = result["synthesized_draft"]
        draft_data = {
            "model_name": draft.model_name,
            "score": draft.score,
            "reasoning": {
                "summary": draft.reasoning.summary,
                "key_arguments": draft.reasoning.key_arguments,
                "regulatory_citations": draft.reasoning.regulatory_citations,
                "vulnerabilities": draft.reasoning.vulnerabilities
            }
        }
        # Add risk_assessment breakdown if available
        if draft.risk_assessment:
            draft_data["risk_assessment"] = {
                "frequency_score": draft.risk_assessment.frequency_score,
                "frequency_rationale": draft.risk_assessment.frequency_rationale,
                "impact_score": draft.risk_assessment.impact_score,
                "impact_rationale": draft.risk_assessment.impact_rationale,
                "final_risk_score": draft.risk_assessment.final_risk_score,
                "risk_classification": draft.risk_assessment.risk_classification
            }
        result_data["output"]["synthesized_draft"] = draft_data
    
    # Serialize draft assessments
    for assessment in result.get("draft_assessments", []):
        assessment_data = {
            "model_name": assessment.model_name,
            "score": assessment.score,
            "reasoning": {
                "summary": assessment.reasoning.summary,
                "key_arguments": assessment.reasoning.key_arguments,
                "regulatory_citations": assessment.reasoning.regulatory_citations,
                "vulnerabilities": assessment.reasoning.vulnerabilities
            }
        }
        # Add risk_assessment breakdown if available
        if assessment.risk_assessment:
            assessment_data["risk_assessment"] = {
                "frequency_score": assessment.risk_assessment.frequency_score,
                "frequency_rationale": assessment.risk_assessment.frequency_rationale,
                "impact_score": assessment.risk_assessment.impact_score,
                "impact_rationale": assessment.risk_assessment.impact_rationale,
                "final_risk_score": assessment.risk_assessment.final_risk_score,
                "risk_classification": assessment.risk_assessment.risk_classification
            }
        result_data["output"]["draft_assessments"].append(assessment_data)
    
    # Serialize critiques
    for critique in result.get("critiques", []):
        result_data["output"]["critiques"].append({
            "challenger_name": critique.challenger_name,
            "is_valid": critique.is_valid,
            "issues": critique.issues,
            "confidence": critique.confidence,
            "recommendation": critique.recommendation
        })

    # Attach conversation log if provided
    if conversation_log:
        result_data["conversation_log"] = conversation_log
    
    # Save to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    return str(filepath)

