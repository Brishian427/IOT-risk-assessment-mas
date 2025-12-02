"""
Configuration and API Key Management
Created: 2025-01-XX
"""

import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration for Multi-Agent System"""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")  # For Challenger B search
    GROK_API_KEY: Optional[str] = os.getenv("GROK_API_KEY")  # Optional, for future use
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    MISTRAL_API_KEY: Optional[str] = os.getenv("MISTRAL_API_KEY")
    
    # Model Configurations
    GENERATOR_TEMPERATURE: float = 0.0  # Maximum analyticity
    CHALLENGER_TEMPERATURE: float = 0.2  # Grounded but creative
    
    # Generator Ensemble Models
    GENERATOR_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "claude-3-5-sonnet-latest",
        "claude-3-opus-20240229",
        "gemini-1.5-pro",
        "deepseek-chat",
        "llama-3.3-70b-versatile",
        "mistral-large-latest",
        "o1-mini",
    ]
    
    # Aggregator Model
    AGGREGATOR_MODEL: str = "claude-3-5-sonnet-latest"
    AGGREGATOR_TEMPERATURE: float = 0.0
    
    # Challenger Models
    CHALLENGER_A_MODEL: str = "gpt-4o"  # o1-preview not available, using gpt-4o directly
    CHALLENGER_A_FALLBACK: str = "gpt-4o"
    CHALLENGER_B_MODEL: str = "deepseek-chat"
    CHALLENGER_C_MODEL: str = "gpt-4o"
    
    # Verifier Model
    VERIFIER_MODEL: str = "claude-3-5-sonnet-latest"
    VERIFIER_TEMPERATURE: float = 0.0
    
    # Workflow Settings
    MAX_REVISIONS: int = 3  # Prevent infinite loops
    
    @classmethod
    def validate_api_keys(cls) -> List[str]:
        """Validate that required API keys are present"""
        missing = []
        
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not cls.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY")
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        if not cls.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")  # Required for Challenger B search
        if not cls.DEEPSEEK_API_KEY:
            missing.append("DEEPSEEK_API_KEY")
        
        return missing

