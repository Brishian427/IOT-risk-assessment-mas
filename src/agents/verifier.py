"""
Verifier - Final arbiter and workflow router
Created: 2025-01-XX
"""

import json
from tqdm import tqdm
from langchain_anthropic import ChatAnthropic
# Node functions don't need explicit Node import in LangGraph

from src.schemas import StateSchema
from src.config import Config
from src.utils.prompt_templates import VERIFIER_PROMPT


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
    
    # Initialize Claude for verification
    llm = ChatAnthropic(
        model=Config.VERIFIER_MODEL,
        temperature=Config.VERIFIER_TEMPERATURE,
        api_key=Config.ANTHROPIC_API_KEY
    )
    
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
        critiques=critiques_text
    )
    
    with tqdm(total=1, desc="Verifier: Routing", unit="step", ncols=80, leave=False) as pbar:
        try:
            response = llm.invoke(prompt)
            pbar.update(1)
            
            content = response.content if hasattr(response, 'content') else str(response)
            
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
    """Conditional edge function: determine if workflow should continue or end"""
    revision_count = state.get("revision_count", 0)
    critiques = state.get("critiques", [])
    
    # Check max revisions - if reached, apply graceful degradation
    if revision_count >= Config.MAX_REVISIONS:
        # Graceful Degradation: Check if we have a "good enough" assessment
        # Get the most recent critiques (last 3, one from each challenger)
        recent_critiques = critiques[-3:] if len(critiques) >= 3 else critiques
        
        if recent_critiques:
            # Count how many challengers passed
            passed_count = sum(
                1 for c in recent_critiques
                if c.is_valid and "accept" in c.recommendation.lower()
            )
            total_challengers = len(recent_critiques)
            
            # If at least 2/3 challengers passed, accept it
            if passed_count >= (total_challengers * 2 / 3):
                return "end"  # Accept the "good enough" assessment
        
        # If not good enough, still end (max revisions reached)
        return "end"
    
    # Check if any critique requires revision
    needs_revision = any(
        not c.is_valid or c.recommendation == "reject"
        for c in critiques
    )
    
    if needs_revision and revision_count < Config.MAX_REVISIONS:
        return "revise"
    else:
        return "end"

