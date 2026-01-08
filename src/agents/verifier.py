"""
Verifier - Final arbiter and workflow router
Created: 2025-01-XX
"""

import json
from tqdm import tqdm
from src.schemas import StateSchema
from src.config import Config
from src.utils.llm_factory import LLMFactory
from src.utils.prompt_templates import VERIFIER_PROMPT
from src.utils.reference_sources import get_reference_sources
from src.utils.conversation_recorder import record
from src.utils.escalation_handler import should_escalate, create_escalation_file, create_escalation_info


def verifier_node(state: StateSchema) -> StateSchema:
    """LangGraph node: Verify critiques and determine if revision is needed"""
    synthesized_draft = state.get("synthesized_draft")
    critiques = state.get("critiques", [])
    revision_count = state.get("revision_count", 0)
    
    # Check max revisions to prevent infinite loops
    if revision_count >= Config.MAX_REVISIONS:
        return {
            "revision_count": revision_count + 1
        }
    
    if not synthesized_draft:
        return {
            "revision_count": revision_count + 1
        }
    
    # Create LLM with transparent fallback
    llm, actual_provider, actual_model, was_fallback = LLMFactory.create(
        model=Config.VERIFIER_MODEL,
        provider=Config.VERIFIER_PROVIDER,
        temperature=Config.VERIFIER_TEMPERATURE,
        fallback_model=Config.VERIFIER_FALLBACK_MODEL,
        fallback_provider=Config.VERIFIER_FALLBACK_PROVIDER,
        context="verifier"
    )
    
    if was_fallback and Config.LOG_FALLBACK_EVENTS:
        print(f"   ℹ️  Verifier using fallback: {actual_provider}/{actual_model}")
    
    # Format critiques for prompt
    critiques_text = "\n\n".join([
        f"Challenger: {c.challenger_name}\n"
        f"Valid: {c.is_valid}\n"
        f"Issues: {', '.join(c.issues)}\n"
        f"Confidence: {c.confidence}\n"
        f"Recommendation: {c.recommendation}"
        for c in critiques
    ])
    
    assessment_text = f"""
Score: {synthesized_draft.score}
Summary: {synthesized_draft.reasoning.summary}
Arguments: {', '.join(synthesized_draft.reasoning.key_arguments)}
"""
    
    prompt = VERIFIER_PROMPT.format(
        assessment=assessment_text,
        critiques=critiques_text,
        reference_sources=get_reference_sources()
    )
    
    with tqdm(total=1, desc="Verifier: Routing", unit="step", ncols=80, leave=False) as pbar:
        try:
            response = llm.invoke(prompt)
            pbar.update(1)
            
            content = response.content if hasattr(response, 'content') else str(response)
            record(
                stage="verifier",
                role="verifier",
                model=f"{actual_provider}/{actual_model}",
                prompt=prompt,
                response=content,
                revision=revision_count,
                extra={
                    "intended_provider": Config.VERIFIER_PROVIDER,
                    "intended_model": Config.VERIFIER_MODEL,
                    "actual_provider": actual_provider,
                    "actual_model": actual_model,
                    "fallback_used": was_fallback
                }
            )
            
            # Parse JSON from response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            data = json.loads(content)
            needs_revision = data.get("needs_revision", False)
        except Exception as e:
            # Record the error for audit completeness
            record(
                stage="verifier",
                role="verifier",
                model=f"{Config.VERIFIER_PROVIDER}/{Config.VERIFIER_MODEL}",
                prompt=prompt,
                response=f"ERROR: {str(e)}",
                revision=revision_count,
                extra={"error": str(e)},
            )
            # On error, check critiques directly
            needs_revision = any(
                not c.is_valid or c.recommendation == "reject"
                for c in critiques
            )
    
    # Increment revision count if revision is needed
    if needs_revision:
        revision_count += 1
    
    return {
        "revision_count": revision_count
    }


def should_continue(state: StateSchema) -> str:
    """
    Conditional edge function: determine if workflow should continue or end.
    
    Convergence Strategy:
    - Always ends when ≥2/3 challengers pass (approved with reserved opinions)
    - Escalates to human if max revisions reached without consensus
    - Falls back to MAX_REVISIONS limit if 2/3 majority is never reached
    """
    revision_count = state.get("revision_count", 0)
    critiques = state.get("critiques", [])
    
    # Get the most recent critiques (last 3, one from each challenger from current round)
    recent_critiques = critiques[-3:] if len(critiques) >= 3 else critiques
    
    if recent_critiques:
        # Count how many challengers passed in the current round
        passed_count = sum(
            1 for c in recent_critiques
            if c.is_valid and "accept" in c.recommendation.lower()
        )
        total_challengers = len(recent_critiques)
        
        # Check if we've reached 2/3 majority (primary convergence mechanism)
        if total_challengers > 0 and passed_count >= (total_challengers * 2 / 3):
            return "end"  # Approved with reserved opinions - end when 2/3 majority reached
    
    # Check if escalation is needed (before max revisions check)
    # Note: Escalation file creation happens in escalation_node to avoid modifying state here
    escalate, reason = should_escalate(state)
    if escalate:
        return "escalate"  # Route to escalation handler
    
    # Fallback: Check max revisions limit (safety mechanism)
    if revision_count >= Config.MAX_REVISIONS:
        # Max revisions reached - check if we should escalate
        escalate, reason = should_escalate(state)
        if escalate:
            return "escalate"
        # Otherwise, force convergence even without 2/3 majority
        return "end"
    
    # Check if any critique requires revision
    needs_revision = any(
        not c.is_valid or c.recommendation == "reject"
        for c in recent_critiques
    )
    
    if needs_revision and revision_count < Config.MAX_REVISIONS:
        return "revise"
    else:
        return "end"

