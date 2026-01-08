"""
Configuration and API Key Management

TRANSPARENCY NOTE:
This system is designed for heterogeneous multi-provider LLM deployment
using the "Council of 9" architecture across 6 provider families.
When API keys are not available for specific providers, the system falls
back to OpenAI models. All fallback events are logged for audit transparency.

Created: 2025-01-XX
"""

import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """
    Configuration for Multi-Agent System
    
    HETEROGENEITY DESIGN - "Council of 9":
    The generator ensemble uses 9 models across 6 provider families:
    - OpenAI (3 models): gpt-4o, gpt-4o-mini, o1-mini
    - Anthropic (2 models): claude-3-5-sonnet, claude-3-opus
    - Google (1 model): gemini-1.5-pro
    - DeepSeek (1 model): deepseek-chat (V3 - Logic powerhouse)
    - Groq (1 model): llama-3.3-70b-versatile
    - Mistral (1 model): mistral-large-latest
    
    Each challenger uses a DIFFERENT provider family to prevent echo chamber.
    Fallback mechanism ensures system operates even with partial API availability.
    """
    
    # ===========================================
    # API KEYS (loaded from environment)
    # ===========================================
    # Required (baseline operation)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Optional - enables full heterogeneity
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    MISTRAL_API_KEY: Optional[str] = os.getenv("MISTRAL_API_KEY")
    
    # For external fact-checking
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # Legacy (kept for backward compatibility)
    GROK_API_KEY: Optional[str] = os.getenv("GROK_API_KEY")  # Optional, for future use
    
    # ===========================================
    # TEMPERATURE SETTINGS
    # ===========================================
    GENERATOR_TEMPERATURE: float = 0.0  # Deterministic for reproducibility
    CHALLENGER_TEMPERATURE: float = 0.2  # Slight variation for critique diversity
    AGGREGATOR_TEMPERATURE: float = 0.0
    VERIFIER_TEMPERATURE: float = 0.0
    
    # ===========================================
    # GENERATOR MODELS - "COUNCIL OF 9"
    # ===========================================
    # Legacy format (backward compatible)
    GENERATOR_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo",
        "gpt-4o-2024-08-06",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-mini-2024-11-20",
    ]
    
    # NEW: Provider-aware generator models (for LLMFactory)
    # Design: 9 models across 6 provider families for genuine diversity
    # Fallback: Each non-OpenAI model falls back to OpenAI equivalent
    GENERATOR_MODELS_WITH_PROVIDERS: List[Dict] = [
        # OpenAI Family (3 models)
        {"model": "gpt-4o", "provider": "openai", "fallback_model": None, "fallback_provider": None},
        {"model": "gpt-4o-mini", "provider": "openai", "fallback_model": None, "fallback_provider": None},
        {"model": "o1-mini", "provider": "openai", "fallback_model": None, "fallback_provider": None},  # Reasoning specialist
        
        # Anthropic Family (2 models)
        {"model": "claude-3-5-sonnet-20241022", "provider": "anthropic", "fallback_model": "gpt-4o", "fallback_provider": "openai"},
        {"model": "claude-3-opus-20240229", "provider": "anthropic", "fallback_model": "gpt-4o", "fallback_provider": "openai"},
        
        # Google Family (1 model)
        {"model": "gemini-1.5-pro", "provider": "google", "fallback_model": "gpt-4o", "fallback_provider": "openai"},
        
        # DeepSeek Family (1 model) - Logic powerhouse
        {"model": "deepseek-chat", "provider": "deepseek", "fallback_model": "gpt-4o", "fallback_provider": "openai"},
        
        # Groq Family (1 model) - Fast inference, latest Llama
        {"model": "llama-3.3-70b-versatile", "provider": "groq", "fallback_model": "gpt-4o", "fallback_provider": "openai"},
        
        # Mistral Family (1 model)
        {"model": "mistral-large-latest", "provider": "mistral", "fallback_model": "gpt-4o", "fallback_provider": "openai"},
    ]
    
    # ===========================================
    # CHALLENGER MODELS - ENFORCED DIVERSITY
    # ===========================================
    # Design: Each challenger MUST use different provider family
    # This prevents echo chamber effects from shared training data
    
    # Challenger A (Logic/Math): OpenAI - strong at structured reasoning
    CHALLENGER_A_MODEL: str = "gpt-4o"
    CHALLENGER_A_PROVIDER: str = "openai"
    CHALLENGER_A_FALLBACK_MODEL: str = "gpt-4o"  # Same (OpenAI is baseline)
    CHALLENGER_A_FALLBACK_PROVIDER: str = "openai"
    
    # Challenger B (Source Verification): Anthropic - careful, citation-aware
    CHALLENGER_B_MODEL: str = "claude-3-5-sonnet-20241022"
    CHALLENGER_B_PROVIDER: str = "anthropic"
    CHALLENGER_B_FALLBACK_MODEL: str = "gpt-4o"
    CHALLENGER_B_FALLBACK_PROVIDER: str = "openai"
    
    # Challenger C (Compliance): Google - broad regulatory knowledge
    CHALLENGER_C_MODEL: str = "gemini-1.5-pro"
    CHALLENGER_C_PROVIDER: str = "google"
    CHALLENGER_C_FALLBACK_MODEL: str = "gpt-4o"
    CHALLENGER_C_FALLBACK_PROVIDER: str = "openai"
    
    # ===========================================
    # AGGREGATOR & VERIFIER
    # ===========================================
    AGGREGATOR_MODEL: str = "claude-3-5-sonnet-20241022"
    AGGREGATOR_PROVIDER: str = "anthropic"
    AGGREGATOR_FALLBACK_MODEL: str = "gpt-4o"
    AGGREGATOR_FALLBACK_PROVIDER: str = "openai"
    
    VERIFIER_MODEL: str = "claude-3-5-sonnet-20241022"
    VERIFIER_PROVIDER: str = "anthropic"
    VERIFIER_FALLBACK_MODEL: str = "gpt-4o"
    VERIFIER_FALLBACK_PROVIDER: str = "openai"
    
    # ===========================================
    # WORKFLOW SETTINGS
    # ===========================================
    MAX_REVISIONS: int = 3  # Prevent infinite loops
    ESCALATION_CONFIDENCE_THRESHOLD: float = 0.7
    
    # ===========================================
    # API TIMEOUT SETTINGS
    # ===========================================
    LLM_REQUEST_TIMEOUT: int = 60  # Timeout in seconds for LLM API calls
    
    # ===========================================
    # TRANSPARENCY FLAGS
    # ===========================================
    LOG_FALLBACK_EVENTS: bool = True  # Always log when fallback is used
    REPORT_HETEROGENEITY_STATUS: bool = True  # Report provider diversity at startup
    
    @classmethod
    def get_generator_configs(cls) -> List[Dict]:
        """
        Get generator configs in provider-aware format.
        Falls back to legacy format if new format not available.
        """
        if hasattr(cls, 'GENERATOR_MODELS_WITH_PROVIDERS'):
            return cls.GENERATOR_MODELS_WITH_PROVIDERS
        else:
            # Convert old format to new format (backward compatibility)
            return [
                {"model": m, "provider": "openai", "fallback_model": None, "fallback_provider": None}
                for m in cls.GENERATOR_MODELS
            ]
    
    @classmethod
    def validate_api_keys(cls) -> List[str]:
        """
        Validate that required API keys are present.
        
        Note: Only OPENAI_API_KEY is strictly required (baseline operation).
        Other keys enable full heterogeneity but system will fallback if missing.
        """
        missing = []
        
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")  # Required for baseline
        
        # Optional keys (warnings only, not errors)
        if not cls.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")  # Required for Challenger B search
        
        return missing

