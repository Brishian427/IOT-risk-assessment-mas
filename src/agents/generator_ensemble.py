"""
Generator Ensemble - 9 parallel models generating risk assessments
Created: 2025-01-XX
"""

import asyncio
import json
from typing import List
from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
# Node functions don't need explicit Node import in LangGraph

from src.schemas import StateSchema, RiskAssessment, ReasoningTrace
from src.config import Config
from src.utils.prompt_templates import GENERATOR_PROMPT


def _get_llm_for_model(model_name: str):
    """Get LLM instance for a specific model"""
    if model_name in ["gpt-4o", "gpt-4o-mini", "o1-mini", "o1-preview"]:
        return ChatOpenAI(
            model=model_name,
            temperature=Config.GENERATOR_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
    elif model_name == "deepseek-chat":
        return ChatOpenAI(
            model="deepseek-chat",
            temperature=Config.GENERATOR_TEMPERATURE,
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.DEEPSEEK_BASE_URL
        )
    elif model_name.startswith("claude"):
        return ChatAnthropic(
            model=model_name,
            temperature=Config.GENERATOR_TEMPERATURE,
            api_key=Config.ANTHROPIC_API_KEY
        )
    elif model_name.startswith("gemini"):
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=Config.GENERATOR_TEMPERATURE,
            google_api_key=Config.GOOGLE_API_KEY
        )
    elif model_name.startswith("llama"):
        # Llama via Groq (OpenAI-compatible)
        return ChatOpenAI(
            model=model_name,
            temperature=Config.GENERATOR_TEMPERATURE,
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
    elif model_name.startswith("mistral"):
        # Mistral via OpenAI-compatible endpoint
        return ChatOpenAI(
            model=model_name,
            temperature=Config.GENERATOR_TEMPERATURE,
            api_key=Config.MISTRAL_API_KEY,
            base_url="https://api.mistral.ai/v1"
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")


async def _generate_assessment(model_name: str, risk_input: str) -> RiskAssessment:
    """Generate a single risk assessment from one model"""
    try:
        llm = _get_llm_for_model(model_name)
        prompt = GENERATOR_PROMPT.format(risk_input=risk_input)
        
        response = await llm.ainvoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
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
        
        # Create RiskAssessment
        return RiskAssessment(
            model_name=model_name,
            score=data["score"],
            reasoning=ReasoningTrace(**data["reasoning"])
        )
    except Exception as e:
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

