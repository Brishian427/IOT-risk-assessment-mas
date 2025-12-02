"""
Pydantic V2 Schemas for Multi-Agent System
Created: 2025-01-XX
"""

from typing import List, TypedDict, Optional, Annotated
from operator import add
from pydantic import BaseModel, Field


class ReasoningTrace(BaseModel):
    """Reasoning trace from risk assessment"""
    summary: str
    key_arguments: List[str]
    regulatory_citations: List[str]  # Specific laws/standards
    vulnerabilities: List[str]  # Specific CVEs or technical flaws


class RiskAssessment(BaseModel):
    """Risk assessment output from a model"""
    model_name: str  # Track which model said this
    score: int = Field(ge=1, le=5)
    reasoning: ReasoningTrace


class Critique(BaseModel):
    """Critique output from challenger agents"""
    challenger_name: str
    is_valid: bool
    issues: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    recommendation: str  # "accept", "reject", "needs_review"


class StateSchema(TypedDict):
    """LangGraph state schema"""
    risk_input: str
    draft_assessments: List[RiskAssessment]
    synthesized_draft: Optional[RiskAssessment]
    critiques: Annotated[List[Critique], add]  # Use reducer for parallel updates
    revision_count: int

