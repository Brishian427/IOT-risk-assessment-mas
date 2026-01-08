"""
Human Escalation Handler - Route failed consensus to human operators
Created: 2025-01-XX
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from src.schemas import StateSchema, EscalationInfo, RiskAssessment, Critique


def ensure_escalation_directory(output_dir: Optional[str] = None) -> Path:
    """Ensure escalation directory exists"""
    if output_dir:
        escalation_dir = Path(output_dir) / "escalations"
    else:
        escalation_dir = Path("escalations")
    escalation_dir.mkdir(parents=True, exist_ok=True)
    return escalation_dir


def create_escalation_file(
    state: StateSchema,
    reason: str,
    output_dir: Optional[str] = None
) -> str:
    """
    Create escalation file for human review.
    
    Args:
        state: Current workflow state
        reason: Reason for escalation
        output_dir: Optional output directory
        
    Returns:
        Path to escalation file
    """
    escalation_dir = ensure_escalation_directory(output_dir)
    
    # Generate timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"escalation_{timestamp}.json"
    filepath = escalation_dir / filename
    
    # Prepare escalation data
    escalation_data = {
        "metadata": {
            "escalation_type": "Human Review Required",
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "risk_input": state.get("risk_input", ""),
            "revision_count": state.get("revision_count", 0),
            "status": "PENDING_HUMAN_REVIEW"
        },
        "escalation_reason": reason,
        "workflow_state": {
            "revision_count": state.get("revision_count", 0),
            "total_assessments": len(state.get("draft_assessments", [])),
            "total_critiques": len(state.get("critiques", []))
        },
        "current_assessment": None,
        "all_assessments": [],
        "critiques": [],
        "human_review_required": {
            "action": "Review this assessment and provide final decision",
            "deadline": None,  # Can be set by external workflow integration
            "priority": "HIGH" if _is_critical_risk(state) else "MEDIUM"
        }
    }
    
    # Serialize synthesized draft
    synthesized_draft = state.get("synthesized_draft")
    if synthesized_draft:
        draft = synthesized_draft
        escalation_data["current_assessment"] = {
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
            escalation_data["current_assessment"]["risk_assessment"] = {
                "frequency_score": draft.risk_assessment.frequency_score,
                "frequency_rationale": draft.risk_assessment.frequency_rationale,
                "impact_score": draft.risk_assessment.impact_score,
                "impact_rationale": draft.risk_assessment.impact_rationale,
                "final_risk_score": draft.risk_assessment.final_risk_score,
                "risk_classification": draft.risk_assessment.risk_classification
            }
    
    # Serialize all draft assessments
    for assessment in state.get("draft_assessments", []):
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
        if assessment.risk_assessment:
            assessment_data["risk_assessment"] = {
                "frequency_score": assessment.risk_assessment.frequency_score,
                "frequency_rationale": assessment.risk_assessment.frequency_rationale,
                "impact_score": assessment.risk_assessment.impact_score,
                "impact_rationale": assessment.risk_assessment.impact_rationale,
                "final_risk_score": assessment.risk_assessment.final_risk_score,
                "risk_classification": assessment.risk_assessment.risk_classification
            }
        escalation_data["all_assessments"].append(assessment_data)
    
    # Serialize critiques
    for critique in state.get("critiques", []):
        escalation_data["critiques"].append({
            "challenger_name": critique.challenger_name,
            "is_valid": critique.is_valid,
            "issues": critique.issues,
            "confidence": critique.confidence,
            "recommendation": critique.recommendation
        })
    
    # Save to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(escalation_data, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


def _is_critical_risk(state: StateSchema) -> bool:
    """Check if current assessment indicates critical risk"""
    synthesized_draft = state.get("synthesized_draft")
    if not synthesized_draft:
        return False
    
    # Check if risk classification is Critical
    if synthesized_draft.risk_assessment:
        return synthesized_draft.risk_assessment.risk_classification.upper() == "CRITICAL"
    
    # Fallback: check legacy score
    return synthesized_draft.score >= 4


def should_escalate(state: StateSchema) -> Tuple[bool, str]:
    """
    Determine if escalation to human is needed.
    
    Returns:
        Tuple of (should_escalate, reason)
    """
    revision_count = state.get("revision_count", 0)
    critiques = state.get("critiques", [])
    synthesized_draft = state.get("synthesized_draft")
    
    # Condition 1: Max revisions reached without consensus
    if revision_count >= 3:  # Config.MAX_REVISIONS
        recent_critiques = critiques[-3:] if len(critiques) >= 3 else critiques
        if recent_critiques:
            passed_count = sum(
                1 for c in recent_critiques
                if c.is_valid and "accept" in c.recommendation.lower()
            )
            total_challengers = len(recent_critiques)
            
            # If less than 2/3 majority after max revisions
            if total_challengers > 0 and passed_count < (total_challengers * 2 / 3):
                return True, f"Max revisions ({revision_count}) reached without 2/3 challenger consensus. Only {passed_count}/{total_challengers} challengers approved."
    
    # Condition 2: Critical risk classification
    if synthesized_draft and synthesized_draft.risk_assessment:
        if synthesized_draft.risk_assessment.risk_classification.upper() == "CRITICAL":
            return True, f"Critical risk classification ({synthesized_draft.risk_assessment.final_risk_score}/25) requires human validation"
    
    # Condition 3: All challengers reject
    if critiques:
        recent_critiques = critiques[-3:] if len(critiques) >= 3 else critiques
        if recent_critiques:
            all_reject = all(
                not c.is_valid or c.recommendation == "reject"
                for c in recent_critiques
            )
            if all_reject:
                return True, "All challengers rejected the assessment. Human review required to resolve conflicts."
    
    return False, ""


def create_escalation_info(
    state: StateSchema,
    reason: str,
    escalation_file: str
) -> EscalationInfo:
    """Create EscalationInfo object"""
    return EscalationInfo(
        escalated=True,
        reason=reason,
        timestamp=datetime.now().isoformat(),
        escalation_file=escalation_file
    )

