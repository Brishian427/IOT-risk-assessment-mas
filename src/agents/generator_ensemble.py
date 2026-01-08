"""
Generator Ensemble - Council of 9 with Heterogeneous Models

DESIGN:
- 9 generator models across 6 provider families (OpenAI, Anthropic, Google, DeepSeek, Groq, Mistral)
- Transparent fallback when providers are unavailable
- Full audit trail of which models actually executed

Created: 2025-01-XX
Updated: 2025-01-XX (LLMFactory integration)
"""

import asyncio
import json
from typing import List, Dict
from tqdm import tqdm
# Node functions don't need explicit Node import in LangGraph

from src.schemas import StateSchema, RiskAssessment, ReasoningTrace
from src.config import Config
from src.utils.llm_factory import LLMFactory
from src.utils.prompt_templates import GENERATOR_PROMPT
from src.utils.reference_sources import get_reference_sources
from src.utils.conversation_recorder import record


async def _generate_assessment(model_config: Dict, risk_input: str, index: int) -> RiskAssessment:
    """Generate a single risk assessment from one model with fallback support"""
    
    model = model_config["model"]
    provider = model_config["provider"]
    fallback_model = model_config.get("fallback_model")
    fallback_provider = model_config.get("fallback_provider")
    
    try:
        # Create LLM using factory (handles fallback transparently)
        llm, actual_provider, actual_model, was_fallback = LLMFactory.create(
            model=model,
            provider=provider,
            temperature=Config.GENERATOR_TEMPERATURE,
            fallback_model=fallback_model,
            fallback_provider=fallback_provider,
            context=f"generator_{index}"
        )
        
        prompt = GENERATOR_PROMPT.format(
            risk_input=risk_input,
            reference_sources=get_reference_sources()
        )
        
        response = await llm.ainvoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Record for audit trail - include both intended and actual model
        model_display = f"{actual_provider}/{actual_model}" + (" [FALLBACK]" if was_fallback else "")
        record(
            stage="generator",
            role="generator",
            model=model_display,
            prompt=prompt,
            response=content,
            revision=0,
            extra={
                "intended_provider": provider,
                "intended_model": model,
                "actual_provider": actual_provider,
                "actual_model": actual_model,
                "fallback_used": was_fallback
            }
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
            model_name=f"{actual_provider}/{actual_model}",
            score=data["score"],
            reasoning=ReasoningTrace(**data["reasoning"]),
            risk_assessment=risk_assessment_breakdown
        )
    except Exception as e:
        # Record the failed attempt for audit completeness
        record(
            stage="generator",
            role="generator",
            model=f"{provider}/{model}",
            prompt=GENERATOR_PROMPT.format(risk_input=risk_input),
            response=f"ERROR: {str(e)}",
            revision=0,
            extra={"error": str(e)}
        )
        # Return a default assessment on error
        return RiskAssessment(
            model_name=f"{provider}/{model} [ERROR]",
            score=3,
            reasoning=ReasoningTrace(
                summary=f"Error generating assessment: {str(e)}",
                key_arguments=[],
                regulatory_citations=[],
                vulnerabilities=[]
            )
        )


def generator_ensemble_node(state: StateSchema) -> StateSchema:
    """
    LangGraph node: Generate assessments from heterogeneous model ensemble.
    
    TRANSPARENCY:
    - Reports provider availability at start
    - Logs all fallback events
    - Includes heterogeneity status in output
    """
    risk_input = state.get("risk_input", "")
    
    # Get generator configs (provider-aware format)
    generator_configs = Config.get_generator_configs()
    
    # Report available providers
    if Config.REPORT_HETEROGENEITY_STATUS:
        available = LLMFactory.get_available_providers()
        print("\n📊 Provider Availability:")
        for provider, is_available in available.items():
            status = "✅ Available" if is_available else "❌ No API Key"
            print(f"   {provider}: {status}")
    
    # Generate all assessments in parallel using asyncio
    async def run_all():
        tasks = [
            _generate_assessment(model_config, risk_input, index)
            for index, model_config in enumerate(generator_configs)
        ]
        
        # Use tqdm for progress tracking
        with tqdm(total=len(tasks), desc="Generator Ensemble", unit="model", ncols=80, leave=False) as pbar:
            # Track completed tasks
            completed = {}
            
            async def with_progress(task, idx, model_config):
                try:
                    result = await task
                    completed[idx] = result
                    model_name = model_config.get("model", "unknown")
                    pbar.set_postfix_str(f"{model_name[:15]:15s} ✓")
                    pbar.update(1)
                    return result
                except Exception as e:
                    completed[idx] = None
                    model_name = model_config.get("model", "unknown")
                    pbar.set_postfix_str(f"{model_name[:15]:15s} ✗")
                    pbar.update(1)
                    raise
            
            # Run all with progress tracking
            results = await asyncio.gather(*[
                with_progress(task, idx, model_config)
                for idx, (task, model_config) in enumerate(zip(tasks, generator_configs))
            ], return_exceptions=True)
            
            # Handle exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error assessment
                    model_config = generator_configs[i]
                    final_results.append(RiskAssessment(
                        model_name=f"{model_config.get('provider', 'unknown')}/{model_config.get('model', 'unknown')} [ERROR]",
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
    
    # Print heterogeneity status
    if Config.REPORT_HETEROGENEITY_STATUS:
        LLMFactory.print_heterogeneity_status()
    
    # Only return fields that are being updated
    return {
        "draft_assessments": assessments
    }

