"""
Challenger A - Logic Consistency Checker
Created: 2025-01-XX
"""

import json
from tqdm import tqdm
from langchain_openai import ChatOpenAI
# Node functions don't need explicit Node import in LangGraph

from src.schemas import StateSchema, Critique
from src.config import Config
from src.utils.prompt_templates import CHALLENGER_A_PROMPT
from src.utils.reference_sources import get_reference_sources
from src.utils.conversation_recorder import record


def challenger_a_node(state: StateSchema) -> StateSchema:
    """LangGraph node: Check logical consistency of synthesized draft"""
    synthesized_draft = state.get("synthesized_draft")
    
    if not synthesized_draft:
        # If no draft, create a critique indicating missing draft
        critique = Critique(
            challenger_name="challenger_a",
            is_valid=False,
            issues=["No synthesized draft available for review"],
            confidence=1.0,
            recommendation="reject"
        )
        critiques = state.get("critiques", [])
        return {
            "critiques": critiques + [critique]
        }
    
    # Initialize LLM (using gpt-4o directly)
    llm = ChatOpenAI(
        model=Config.CHALLENGER_A_MODEL,
        temperature=Config.CHALLENGER_TEMPERATURE,
        api_key=Config.OPENAI_API_KEY
    )
    
    # Format reasoning for prompt
    reasoning_text = f"""
Summary: {synthesized_draft.reasoning.summary}
Arguments: {', '.join(synthesized_draft.reasoning.key_arguments)}
"""
    
    # Format risk assessment breakdown if available
    risk_assessment_text = "Not provided"
    if synthesized_draft.risk_assessment:
        ra = synthesized_draft.risk_assessment
        risk_assessment_text = f"""
Frequency Score: {ra.frequency_score}/5
Frequency Rationale: {ra.frequency_rationale}
Impact Score: {ra.impact_score}/5
Impact Rationale: {ra.impact_rationale}
Final Risk Score: {ra.final_risk_score}/25
Risk Classification: {ra.risk_classification}
Calculation Check: {ra.frequency_score} × {ra.impact_score} = {ra.frequency_score * ra.impact_score} (Expected: {ra.final_risk_score})
"""
    else:
        risk_assessment_text = "Not provided (legacy format - only legacy score available)"
    
    prompt = CHALLENGER_A_PROMPT.format(
        score=synthesized_draft.score,
        reasoning=reasoning_text,
        risk_assessment=risk_assessment_text,
        reference_sources=get_reference_sources()
    )
    
    with tqdm(total=1, desc="Challenger A: Checking", unit="step", ncols=80, leave=False) as pbar:
        try:
            response = llm.invoke(prompt)
            pbar.update(1)
            
            content = response.content if hasattr(response, 'content') else str(response)
            record(
                stage="challenger_a",
                role="challenger",
                model=Config.CHALLENGER_A_MODEL,
                prompt=prompt,
                response=content,
                revision=state.get("revision_count", 0),
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
                challenger_name="challenger_a",
                is_valid=data.get("is_valid", True),
                issues=data.get("issues", []),
                confidence=data.get("confidence", 0.5),
                recommendation=data.get("recommendation", "needs_review")
            )
        except Exception as e:
            # Record the error for audit completeness
            record(
                stage="challenger_a",
                role="challenger",
                model=Config.CHALLENGER_A_MODEL,
                prompt=prompt,
                response=f"ERROR: {str(e)}",
                revision=state.get("revision_count", 0),
            )
            # On error, create a critique indicating review failure
            critique = Critique(
                challenger_name="challenger_a",
                is_valid=False,
                issues=[f"Error during logic check: {str(e)}"],
                confidence=0.0,
                recommendation="needs_review"
            )
    
    critiques = state.get("critiques", [])
    return {
        "critiques": critiques + [critique]
    }

