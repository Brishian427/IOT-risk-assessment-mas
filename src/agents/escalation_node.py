"""
Escalation Node - Handle human escalation
Created: 2025-01-XX
"""

from src.schemas import StateSchema
from src.utils.conversation_recorder import record
from src.utils.escalation_handler import should_escalate, create_escalation_file, create_escalation_info


def escalation_node(state: StateSchema) -> StateSchema:
    """
    LangGraph node: Handle human escalation.
    
    This node is reached when:
    1. Max revisions reached without consensus
    2. Critical risk classification
    3. All challengers reject
    
    This node creates the escalation file and marks state for human review.
    """
    # Check if escalation is needed and create escalation file
    escalate, reason = should_escalate(state)
    
    if escalate:
        # Create escalation file
        escalation_file = create_escalation_file(state, reason)
        escalation_info = create_escalation_info(state, reason, escalation_file)
        
        # Log escalation event
        record(
            stage="escalation",
            role="escalation_handler",
            model="human_review",
            prompt=f"Escalation triggered: {reason}",
            response=f"Escalation file created: {escalation_file}",
            revision=state.get("revision_count", 0),
            extra={
                "escalation_reason": reason,
                "escalation_file": escalation_file,
                "timestamp": escalation_info.timestamp
            }
        )
        
        # Print escalation notice
        print("\n" + "="*80)
        print("⚠️  HUMAN ESCALATION REQUIRED")
        print("="*80)
        print(f"Reason: {reason}")
        print(f"Escalation file: {escalation_file}")
        print("\nA human operator must review this assessment before final decision.")
        print("="*80 + "\n")
        
        # Return escalation info in state
        return {
            "escalation": escalation_info
        }
    
    # No escalation needed (shouldn't reach here, but handle gracefully)
    return {}

