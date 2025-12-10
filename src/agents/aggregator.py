"""
Aggregator - Synthesize unified draft from 9 assessments
Created: 2025-01-XX
"""

import json
from tqdm import tqdm
from langchain_openai import ChatOpenAI
# Node functions don't need explicit Node import in LangGraph

from src.schemas import StateSchema, RiskAssessment, ReasoningTrace
from src.config import Config
from src.utils.prompt_templates import AGGREGATOR_PROMPT, AGGREGATOR_REVISION_PROMPT
from src.utils.reference_sources import get_reference_sources
from src.utils.conversation_recorder import record


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
        # Initialize OpenAI for aggregation
        llm = ChatOpenAI(
            model=Config.AGGREGATOR_MODEL,
            temperature=Config.AGGREGATOR_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
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
            
            # Format previous risk assessment breakdown if available
            if previous_draft.risk_assessment:
                ra = previous_draft.risk_assessment
                previous_text += f"""
Risk Assessment Breakdown:
  Frequency Score: {ra.frequency_score}/5
  Frequency Rationale: {ra.frequency_rationale}
  Impact Score: {ra.impact_score}/5
  Impact Rationale: {ra.impact_rationale}
  Final Risk Score: {ra.final_risk_score}/25
  Risk Classification: {ra.risk_classification}
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
                critiques=critiques_text,
                reference_sources=get_reference_sources()
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
                + (f"\nRisk Assessment: Frequency={assess.risk_assessment.frequency_score}, Impact={assess.risk_assessment.impact_score}, Final={assess.risk_assessment.final_risk_score}, Classification={assess.risk_assessment.risk_classification}" if assess.risk_assessment else "")
                for assess in draft_assessments
            ])
            pbar.update(0.3)
            pbar.set_description("Aggregator: Synthesizing")
            prompt = AGGREGATOR_PROMPT.format(
                assessments=assessments_text,
                reference_sources=get_reference_sources()
            )
        
        try:
            response = llm.invoke(prompt)
            pbar.update(0.7)
            
            content = response.content if hasattr(response, 'content') else str(response)
            record(
                stage="aggregator",
                role="aggregator",
                model=Config.AGGREGATOR_MODEL,
                prompt=prompt,
                response=content,
                revision=revision_count,
                extra={"mode": "revision" if is_revision else "initial"},
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
            
            # Extract risk_assessment breakdown if available
            risk_assessment_breakdown = None
            if "risk_assessment" in data:
                from src.schemas import RiskAssessmentBreakdown
                try:
                    risk_assessment_breakdown = RiskAssessmentBreakdown(**data["risk_assessment"])
                    # Validate calculation
                    expected_final = risk_assessment_breakdown.frequency_score * risk_assessment_breakdown.impact_score
                    if risk_assessment_breakdown.final_risk_score != expected_final:
                        # Auto-correct calculation error
                        risk_assessment_breakdown.final_risk_score = expected_final
                except Exception as e:
                    # If parsing fails, continue without breakdown (backward compatibility)
                    pass
            
            # Create synthesized RiskAssessment
            synthesized_draft = RiskAssessment(
                model_name="aggregated",
                score=data["score"],
                reasoning=ReasoningTrace(**data["reasoning"]),
                risk_assessment=risk_assessment_breakdown
            )
            
            # Only return fields that are being updated
            return {
                "synthesized_draft": synthesized_draft
            }
        except Exception as e:
            # Record the error for audit completeness
            record(
                stage="aggregator",
                role="aggregator",
                model=Config.AGGREGATOR_MODEL,
                prompt=prompt,
                response=f"ERROR: {str(e)}",
                revision=revision_count,
                extra={"mode": "revision" if is_revision else "initial"},
            )
            # On error, use first assessment as fallback
            return {
                "synthesized_draft": draft_assessments[0] if draft_assessments else None
            }

