"""
Challenger C - Safety & Compliance Checker
Created: 2025-01-XX
"""

import json
from tqdm import tqdm
from src.schemas import StateSchema, Critique
from src.config import Config
from src.utils.llm_factory import LLMFactory
from src.utils.prompt_templates import CHALLENGER_C_PROMPT
from src.utils.reference_sources import get_reference_sources
from src.utils.conversation_recorder import record


def challenger_c_node(state: StateSchema) -> StateSchema:
    """LangGraph node: Check safety and compliance constraints"""
    synthesized_draft = state.get("synthesized_draft")
    
    if not synthesized_draft:
        critique = Critique(
            challenger_name="challenger_c",
            is_valid=False,
            issues=["No synthesized draft available for review"],
            confidence=1.0,
            recommendation="reject"
        )
        critiques = state.get("critiques", [])
        return {
            "critiques": critiques + [critique]
        }
    
    # Create LLM with transparent fallback
    llm, actual_provider, actual_model, was_fallback = LLMFactory.create(
        model=Config.CHALLENGER_C_MODEL,
        provider=Config.CHALLENGER_C_PROVIDER,
        temperature=Config.CHALLENGER_TEMPERATURE,
        fallback_model=Config.CHALLENGER_C_FALLBACK_MODEL,
        fallback_provider=Config.CHALLENGER_C_FALLBACK_PROVIDER,
        context="challenger_c"
    )
    
    if was_fallback and Config.LOG_FALLBACK_EVENTS:
        print(f"   ℹ️  Challenger C using fallback: {actual_provider}/{actual_model}")
    
    # Format reasoning for prompt
    reasoning_text = f"""
Summary: {synthesized_draft.reasoning.summary}
Arguments: {', '.join(synthesized_draft.reasoning.key_arguments)}
Regulatory Citations: {', '.join(synthesized_draft.reasoning.regulatory_citations)}
Vulnerabilities: {', '.join(synthesized_draft.reasoning.vulnerabilities)}
"""
    
    prompt = CHALLENGER_C_PROMPT.format(
        score=synthesized_draft.score,
        reasoning=reasoning_text,
        reference_sources=get_reference_sources()
    )
    
    with tqdm(total=1, desc="Challenger C: Checking", unit="step", ncols=80, leave=False) as pbar:
        try:
            response = llm.invoke(prompt)
            pbar.update(1)
            
            content = response.content if hasattr(response, 'content') else str(response)
            record(
                stage="challenger_c",
                role="challenger",
                model=f"{actual_provider}/{actual_model}",
                prompt=prompt,
                response=content,
                revision=state.get("revision_count", 0),
                extra={
                    "intended_provider": Config.CHALLENGER_C_PROVIDER,
                    "intended_model": Config.CHALLENGER_C_MODEL,
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
            
            critique = Critique(
                challenger_name="challenger_c",
                is_valid=data.get("is_valid", True),
                issues=data.get("issues", []),
                confidence=data.get("confidence", 0.5),
                recommendation=data.get("recommendation", "needs_review")
            )
        except Exception as e:
            # Record the error for audit completeness
            record(
                stage="challenger_c",
                role="challenger",
                model=f"{Config.CHALLENGER_C_PROVIDER}/{Config.CHALLENGER_C_MODEL}",
                prompt=prompt,
                response=f"ERROR: {str(e)}",
                revision=state.get("revision_count", 0),
                extra={"error": str(e)},
            )
            # On error, create a critique indicating review failure
            critique = Critique(
                challenger_name="challenger_c",
                is_valid=False,
                issues=[f"Error during compliance check: {str(e)}"],
                confidence=0.0,
                recommendation="needs_review"
            )
    
    critiques = state.get("critiques", [])
    return {
        "critiques": critiques + [critique]
    }

