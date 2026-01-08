"""
LLM Factory - Multi-Provider Model Instantiation with Transparent Fallback

TRANSPARENCY DESIGN:
This factory supports genuine heterogeneity across 6 LLM provider families
("Council of 9" architecture) while implementing graceful fallback when 
API keys are unavailable. ALL fallback events are explicitly logged for 
audit transparency.

SUPPORTED PROVIDERS:
1. OpenAI (gpt-4o, gpt-4o-mini, o1-mini)
2. Anthropic (claude-3-5-sonnet, claude-3-opus)
3. Google (gemini-1.5-pro)
4. DeepSeek (deepseek-chat)
5. Groq (llama-3.3-70b-versatile)
6. Mistral (mistral-large-latest)

The system will:
1. Attempt to instantiate the requested provider's model
2. If API key is missing, log a WARNING and fall back to specified fallback
3. Track and report which providers were actually used vs. intended
4. Generate a heterogeneity report for audit purposes

Created: 2025-01-XX
"""

from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
import json

# LangChain imports - OpenAI is always required
from langchain_openai import ChatOpenAI

# Conditional imports for optional providers
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    ChatAnthropic = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    ChatGoogleGenerativeAI = None

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    ChatGroq = None

try:
    from langchain_mistralai import ChatMistralAI
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    ChatMistralAI = None

# DeepSeek uses OpenAI-compatible API
DEEPSEEK_AVAILABLE = True  # Uses ChatOpenAI with custom base_url

from src.config import Config

config = Config()


@dataclass
class FallbackEvent:
    """Record of a fallback event for audit transparency"""
    timestamp: str
    intended_provider: str
    intended_model: str
    actual_provider: str
    actual_model: str
    reason: str


@dataclass
class HeterogeneityReport:
    """Report on actual model heterogeneity achieved"""
    intended_providers: List[str]
    actual_providers: List[str]
    fallback_events: List[FallbackEvent]
    heterogeneity_achieved: bool
    diversity_score: float  # 0-1, where 1 = all intended providers used
    message: str


class LLMFactory:
    """
    Factory for creating LLM instances with transparent fallback.
    
    SUPPORTED PROVIDERS (6 families):
    - openai: GPT-4o, GPT-4o-mini, o1-mini
    - anthropic: Claude 3.5 Sonnet, Claude 3 Opus
    - google: Gemini 1.5 Pro
    - deepseek: DeepSeek Chat (V3)
    - groq: Llama 3.3 70B
    - mistral: Mistral Large
    
    AUDIT TRANSPARENCY:
    - All instantiation attempts are logged
    - Fallback events are recorded with full context
    - Heterogeneity report available for audit
    """
    
    # Track all fallback events for audit (class variables)
    _fallback_events: List[FallbackEvent] = []
    _instantiation_log: List[Dict] = []
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """
        Check which providers have valid API keys and libraries configured.
        
        Returns:
            Dict mapping provider name to availability status
        """
        return {
            "openai": bool(config.OPENAI_API_KEY),
            "anthropic": bool(config.ANTHROPIC_API_KEY) and ANTHROPIC_AVAILABLE,
            "google": bool(config.GOOGLE_API_KEY) and GOOGLE_AVAILABLE,
            "deepseek": bool(config.DEEPSEEK_API_KEY) and DEEPSEEK_AVAILABLE,
            "groq": bool(config.GROQ_API_KEY) and GROQ_AVAILABLE,
            "mistral": bool(config.MISTRAL_API_KEY) and MISTRAL_AVAILABLE,
        }
    
    @classmethod
    def create(
        cls,
        model: str,
        provider: str,
        temperature: float = 0.0,
        fallback_model: Optional[str] = None,
        fallback_provider: Optional[str] = None,
        context: str = "unknown"  # For logging: "generator_0", "challenger_a", etc.
    ) -> Tuple:
        """
        Create an LLM instance with transparent fallback.
        
        Args:
            model: Model name (e.g., "gpt-4o", "claude-3-5-sonnet-20241022", "deepseek-chat")
            provider: Provider name ("openai", "anthropic", "google", "deepseek", "groq", "mistral")
            temperature: Sampling temperature
            fallback_model: Model to use if primary fails
            fallback_provider: Provider for fallback model
            context: Context string for logging (which agent is this for)
            
        Returns:
            Tuple of (LLM instance, actual_provider, actual_model, was_fallback)
        """
        available = cls.get_available_providers()
        
        # Check if requested provider is available
        if provider in available and available[provider]:
            try:
                llm = cls._instantiate(model, provider, temperature)
                cls._log_instantiation(context, provider, model, provider, model, False)
                return llm, provider, model, False
            except Exception as e:
                print(f"⚠️  [{context}] Failed to instantiate {provider}/{model}: {e}")
                # Fall through to fallback
        
        # Provider not available or failed - use fallback
        if fallback_model and fallback_provider:
            reason = f"API key missing for {provider}" if not available.get(provider) else f"Instantiation failed for {provider}/{model}"
            
            # Record fallback event
            fallback_event = FallbackEvent(
                timestamp=datetime.now().isoformat(),
                intended_provider=provider,
                intended_model=model,
                actual_provider=fallback_provider,
                actual_model=fallback_model,
                reason=reason
            )
            cls._fallback_events.append(fallback_event)
            
            # Log transparently
            print(f"⚠️  [{context}] FALLBACK: {provider}/{model} → {fallback_provider}/{fallback_model}")
            print(f"    Reason: {reason}")
            
            try:
                llm = cls._instantiate(fallback_model, fallback_provider, temperature)
                cls._log_instantiation(context, provider, model, fallback_provider, fallback_model, True)
                return llm, fallback_provider, fallback_model, True
            except Exception as e:
                raise RuntimeError(f"Both primary and fallback failed: {e}")
        
        # No fallback specified - try OpenAI as universal fallback
        if provider != "openai" and available.get("openai"):
            print(f"⚠️  [{context}] UNIVERSAL FALLBACK: {provider}/{model} → openai/gpt-4o")
            
            fallback_event = FallbackEvent(
                timestamp=datetime.now().isoformat(),
                intended_provider=provider,
                intended_model=model,
                actual_provider="openai",
                actual_model="gpt-4o",
                reason=f"No specific fallback configured; using OpenAI as universal fallback"
            )
            cls._fallback_events.append(fallback_event)
            
            llm = cls._instantiate("gpt-4o", "openai", temperature)
            cls._log_instantiation(context, provider, model, "openai", "gpt-4o", True)
            return llm, "openai", "gpt-4o", True
        
        raise RuntimeError(f"Cannot instantiate any model. Check API keys.")
    
    @classmethod
    def _instantiate(cls, model: str, provider: str, temperature: float):
        """Internal method to create LLM instance for each provider"""
        
        # Get timeout from config (default 60 seconds)
        timeout = getattr(config, 'LLM_REQUEST_TIMEOUT', 60)
        
        if provider == "openai":
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=config.OPENAI_API_KEY,
                request_timeout=timeout,
            )
        
        elif provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("langchain-anthropic not installed. Run: pip install langchain-anthropic")
            if not config.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                api_key=config.ANTHROPIC_API_KEY,
                timeout=timeout,  # Anthropic uses 'timeout' parameter
            )
        
        elif provider == "google":
            if not GOOGLE_AVAILABLE:
                raise ImportError("langchain-google-genai not installed. Run: pip install langchain-google-genai")
            if not config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not configured")
            return ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                google_api_key=config.GOOGLE_API_KEY,
                timeout=timeout,  # Google uses 'timeout' parameter
            )
        
        elif provider == "deepseek":
            # DeepSeek uses OpenAI-compatible API with custom base URL
            if not config.DEEPSEEK_API_KEY:
                raise ValueError("DEEPSEEK_API_KEY not configured")
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=config.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com/v1",
                request_timeout=timeout,
            )
        
        elif provider == "groq":
            if not GROQ_AVAILABLE:
                raise ImportError("langchain-groq not installed. Run: pip install langchain-groq")
            if not config.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not configured")
            return ChatGroq(
                model=model,
                temperature=temperature,
                api_key=config.GROQ_API_KEY,
                timeout=timeout,  # Groq uses 'timeout' parameter
            )
        
        elif provider == "mistral":
            if not MISTRAL_AVAILABLE:
                raise ImportError("langchain-mistralai not installed. Run: pip install langchain-mistralai")
            if not config.MISTRAL_API_KEY:
                raise ValueError("MISTRAL_API_KEY not configured")
            return ChatMistralAI(
                model=model,
                temperature=temperature,
                api_key=config.MISTRAL_API_KEY,
                timeout=timeout,  # Mistral uses 'timeout' parameter
            )
        
        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: openai, anthropic, google, deepseek, groq, mistral")
    
    @classmethod
    def _log_instantiation(cls, context, intended_provider, intended_model, 
                          actual_provider, actual_model, was_fallback):
        """Log instantiation for audit trail"""
        cls._instantiation_log.append({
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "intended": f"{intended_provider}/{intended_model}",
            "actual": f"{actual_provider}/{actual_model}",
            "fallback_used": was_fallback
        })
    
    @classmethod
    def get_heterogeneity_report(cls) -> HeterogeneityReport:
        """
        Generate a report on model heterogeneity for audit purposes.
        
        Returns:
            HeterogeneityReport with details on intended vs actual provider usage
        """
        if not cls._instantiation_log:
            return HeterogeneityReport(
                intended_providers=[],
                actual_providers=[],
                fallback_events=[],
                heterogeneity_achieved=False,
                diversity_score=0.0,
                message="No models instantiated yet"
            )
        
        intended = set(log["intended"].split("/")[0] for log in cls._instantiation_log)
        actual = set(log["actual"].split("/")[0] for log in cls._instantiation_log)
        
        # Calculate diversity score
        diversity_score = len(actual) / max(len(intended), 1)
        heterogeneity_achieved = len(actual) >= 2
        
        if len(actual) == 1:
            message = f"⚠️  NO HETEROGENEITY: All models using {list(actual)[0]} only"
        elif len(actual) == len(intended):
            message = f"✅ FULL HETEROGENEITY: All {len(actual)} intended providers active"
        else:
            message = f"⚠️  PARTIAL HETEROGENEITY: {len(actual)}/{len(intended)} providers active ({actual})"
        
        return HeterogeneityReport(
            intended_providers=list(intended),
            actual_providers=list(actual),
            fallback_events=cls._fallback_events,
            heterogeneity_achieved=heterogeneity_achieved,
            diversity_score=diversity_score,
            message=message
        )
    
    @classmethod
    def print_heterogeneity_status(cls):
        """Print heterogeneity status to console"""
        report = cls.get_heterogeneity_report()
        print("\n" + "="*60)
        print("MODEL HETEROGENEITY STATUS")
        print("="*60)
        print(f"Intended providers: {report.intended_providers}")
        print(f"Actual providers:   {report.actual_providers}")
        print(f"Diversity score:    {report.diversity_score:.1%}")
        print(f"Status:             {report.message}")
        if report.fallback_events:
            print(f"\nFallback events ({len(report.fallback_events)}):")
            for event in report.fallback_events:
                print(f"  - {event.intended_provider}/{event.intended_model} → {event.actual_provider}/{event.actual_model}")
                print(f"    Reason: {event.reason}")
        print("="*60 + "\n")
    
    @classmethod
    def export_audit_log(cls, filepath: str):
        """Export full audit log to JSON file"""
        audit_data = {
            "generated_at": datetime.now().isoformat(),
            "heterogeneity_report": {
                "intended_providers": cls.get_heterogeneity_report().intended_providers,
                "actual_providers": cls.get_heterogeneity_report().actual_providers,
                "diversity_score": cls.get_heterogeneity_report().diversity_score,
                "heterogeneity_achieved": cls.get_heterogeneity_report().heterogeneity_achieved,
                "message": cls.get_heterogeneity_report().message
            },
            "fallback_events": [
                {
                    "timestamp": e.timestamp,
                    "intended": f"{e.intended_provider}/{e.intended_model}",
                    "actual": f"{e.actual_provider}/{e.actual_model}",
                    "reason": e.reason
                }
                for e in cls._fallback_events
            ],
            "instantiation_log": cls._instantiation_log
        }
        
        with open(filepath, "w") as f:
            json.dump(audit_data, f, indent=2)
        
        print(f"📋 Audit log exported to: {filepath}")
    
    @classmethod
    def reset_logs(cls):
        """Reset all logs (for testing)"""
        cls._fallback_events = []
        cls._instantiation_log = []


# Convenience function
def get_llm(
    model: str, 
    provider: str, 
    temperature: float = 0.0,
    fallback_model: Optional[str] = None,
    fallback_provider: Optional[str] = None,
    context: str = "unknown"
):
    """
    Convenience function for creating LLM instances.
    
    Returns just the LLM instance (not the full tuple).
    For full audit information, use LLMFactory.create() directly.
    """
    llm, _, _, _ = LLMFactory.create(
        model, provider, temperature, 
        fallback_model, fallback_provider, context
    )
    return llm

