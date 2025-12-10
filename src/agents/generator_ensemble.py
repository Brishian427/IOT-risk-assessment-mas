"""
Generator Ensemble - 9 parallel models generating risk assessments
Created: 2025-01-XX
"""

import asyncio
import json
from typing import List
from tqdm import tqdm
from langchain_openai import ChatOpenAI
# Node functions don't need explicit Node import in LangGraph

from src.schemas import StateSchema, RiskAssessment, ReasoningTrace
from src.config import Config
from src.utils.prompt_templates import GENERATOR_PROMPT
from src.utils.reference_sources import get_reference_sources
from src.utils.conversation_recorder import record


def _get_llm_for_model(model_name: str):
    """Get LLM instance for a specific model"""
    # All OpenAI stack models use the same client
    return ChatOpenAI(
        model=model_name,
        temperature=Config.GENERATOR_TEMPERATURE,
        api_key=Config.OPENAI_API_KEY
    )


async def _generate_assessment(model_name: str, risk_input: str) -> RiskAssessment:
    """Generate a single risk assessment from one model"""
    try:
        llm = _get_llm_for_model(model_name)
        prompt = GENERATOR_PROMPT.format(
            risk_input=risk_input,
            reference_sources=get_reference_sources()
        )
        
        response = await llm.ainvoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        record(
            stage="generator",
            role="generator",
            model=model_name,
            prompt=prompt,
            response=content,
            revision=0,
        )
        
        # Parse JSON from response
        # Try to extract JSON from markdown code blocks if present
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
        
        # Create RiskAssessment
        return RiskAssessment(
            model_name=model_name,
            score=data["score"],
            reasoning=ReasoningTrace(**data["reasoning"]),
            risk_assessment=risk_assessment_breakdown
        )
    except Exception as e:
        # Record the failed attempt for audit completeness
        record(
            stage="generator",
            role="generator",
            model=model_name,
            prompt=GENERATOR_PROMPT.format(risk_input=risk_input),
            response=f"ERROR: {str(e)}",
            revision=0,
        )
        # Return a default assessment on error
        return RiskAssessment(
            model_name=model_name,
            score=3,
            reasoning=ReasoningTrace(
                summary=f"Error generating assessment: {str(e)}",
                key_arguments=[],
                regulatory_citations=[],
                vulnerabilities=[]
            )
        )


def generator_ensemble_node(state: StateSchema) -> StateSchema:
    """LangGraph node: Generate 9 parallel risk assessments"""
    risk_input = state["risk_input"]
    
    # Generate all assessments in parallel using asyncio
    async def run_all():
        tasks = [
            _generate_assessment(model_name, risk_input)
            for model_name in Config.GENERATOR_MODELS
        ]
        
        # Use tqdm for progress tracking
        with tqdm(total=len(tasks), desc="Generator Ensemble", unit="model", ncols=80, leave=False) as pbar:
            # Track completed tasks
            completed = {}
            
            async def with_progress(task, idx, model_name):
                try:
                    result = await task
                    completed[idx] = result
                    pbar.set_postfix_str(f"{model_name[:15]:15s} ✓")
                    pbar.update(1)
                    return result
                except Exception as e:
                    completed[idx] = None
                    pbar.set_postfix_str(f"{model_name[:15]:15s} ✗")
                    pbar.update(1)
                    raise
            
            # Run all with progress tracking
            results = await asyncio.gather(*[
                with_progress(task, idx, model_name)
                for idx, (task, model_name) in enumerate(zip(tasks, Config.GENERATOR_MODELS))
            ], return_exceptions=True)
            
            # Handle exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error assessment
                    final_results.append(RiskAssessment(
                        model_name=Config.GENERATOR_MODELS[i],
                        score=3,
                        reasoning=ReasoningTrace(
                            summary=f"Error: {str(result)}",
                            key_arguments=[],
                            regulatory_citations=[],
                            vulnerabilities=[]
                        )
                    ))
                else:
                    final_results.append(result)
            
            return final_results
    
    # Run async tasks synchronously
    assessments = asyncio.run(run_all())
    
    # Only return fields that are being updated
    return {
        "draft_assessments": assessments
    }

