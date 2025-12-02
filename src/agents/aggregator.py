"""
Aggregator - Synthesize unified draft from 9 assessments
Created: 2025-01-XX
"""

import json
from tqdm import tqdm
from langchain_anthropic import ChatAnthropic
# Node functions don't need explicit Node import in LangGraph

from src.schemas import StateSchema, RiskAssessment, ReasoningTrace
from src.config import Config
from src.utils.prompt_templates import AGGREGATOR_PROMPT, AGGREGATOR_REVISION_PROMPT


def aggregator_node(state: StateSchema) -> StateSchema:
    """LangGraph node: Synthesize unified draft from 9 assessments, or revise based on critiques"""
    draft_assessments = state["draft_assessments"]
    critiques = state.get("critiques", [])
    revision_count = state.get("revision_count", 0)
    previous_draft = state.get("synthesized_draft")
    
    if not draft_assessments:
        # If no assessments, create empty draft
        return {
            "synthesized_draft": None
        }
    
    # Determine if this is a revision cycle
    is_revision = revision_count > 0 and previous_draft is not None and len(critiques) > 0
    
    with tqdm(total=1, desc="Aggregator", unit="step", ncols=80, leave=False) as pbar:
        # Initialize Claude for aggregation
        llm = ChatAnthropic(
            model=Config.AGGREGATOR_MODEL,
            temperature=Config.AGGREGATOR_TEMPERATURE,
            api_key=Config.ANTHROPIC_API_KEY
        )
        
        if is_revision:
            # Use revision prompt
            pbar.set_description("Aggregator: Revising")
            
            # Format previous assessment
            previous_text = f"""
Score: {previous_draft.score}
Summary: {previous_draft.reasoning.summary}
Arguments: {', '.join(previous_draft.reasoning.key_arguments)}
Citations: {', '.join(previous_draft.reasoning.regulatory_citations)}
Vulnerabilities: {', '.join(previous_draft.reasoning.vulnerabilities)}
"""
            
            # Format critiques (get the most recent set - last 3 critiques)
            recent_critiques = critiques[-3:] if len(critiques) >= 3 else critiques
            critiques_text = "\n\n".join([
                f"Challenger {c.challenger_name}:\n"
                f"  Valid: {c.is_valid}\n"
                f"  Issues: {', '.join(c.issues)}\n"
                f"  Confidence: {c.confidence}\n"
                f"  Recommendation: {c.recommendation}"
                for c in recent_critiques
            ])
            
            prompt = AGGREGATOR_REVISION_PROMPT.format(
                previous_assessment=previous_text,
                critiques=critiques_text
            )
        else:
            # Use initial synthesis prompt
            pbar.set_description("Aggregator: Formatting")
            assessments_text = "\n\n".join([
                f"Model: {assess.model_name}\n"
                f"Score: {assess.score}\n"
                f"Summary: {assess.reasoning.summary}\n"
                f"Arguments: {', '.join(assess.reasoning.key_arguments)}\n"
                f"Citations: {', '.join(assess.reasoning.regulatory_citations)}\n"
                f"Vulnerabilities: {', '.join(assess.reasoning.vulnerabilities)}"
                for assess in draft_assessments
            ])
            pbar.update(0.3)
            pbar.set_description("Aggregator: Synthesizing")
            prompt = AGGREGATOR_PROMPT.format(assessments=assessments_text)
        
        try:
            response = llm.invoke(prompt)
            pbar.update(0.7)
            
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
            
            # Create synthesized RiskAssessment
            synthesized_draft = RiskAssessment(
                model_name="aggregated",
                score=data["score"],
                reasoning=ReasoningTrace(**data["reasoning"])
            )
            
            # Only return fields that are being updated
            return {
                "synthesized_draft": synthesized_draft
            }
        except Exception as e:
            # On error, use first assessment as fallback
            return {
                "synthesized_draft": draft_assessments[0] if draft_assessments else None
            }

