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
    
    prompt = CHALLENGER_A_PROMPT.format(
        score=synthesized_draft.score,
        reasoning=reasoning_text
    )
    
    with tqdm(total=1, desc="Challenger A: Checking", unit="step", ncols=80, leave=False) as pbar:
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
            
            critique = Critique(
                challenger_name="challenger_a",
                is_valid=data.get("is_valid", True),
                issues=data.get("issues", []),
                confidence=data.get("confidence", 0.5),
                recommendation=data.get("recommendation", "needs_review")
            )
        except Exception as e:
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

