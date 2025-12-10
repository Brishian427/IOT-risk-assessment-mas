"""
Logging System - Record complete assessment workflow
Created: 2025-01-XX
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class AssessmentLogger:
    """Logger for tracking complete assessment workflows"""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize assessment logger
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("assessment_workflow")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"assessment_iot_risk_{timestamp}.log"
        self.log_file = log_file
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
            
            # Also log to console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def log_start(self, risk_input: str):
        """Log workflow start"""
        self.logger.info("=" * 80)
        self.logger.info("Assessment for IoT Risk")
        self.logger.info("RISK ASSESSMENT WORKFLOW STARTED")
        self.logger.info("=" * 80)
        self.logger.info(f"Input Scenario:\n{risk_input}\n")
    
    def log_generator_ensemble(self, assessments_count: int):
        """Log generator ensemble completion"""
        self.logger.info(f"[Generator Ensemble] Generated {assessments_count} initial assessments")
    
    def log_aggregator(self, mode: str = "initial"):
        """Log aggregator operation"""
        if mode == "initial":
            self.logger.info("[Aggregator] Synthesising unified draft from initial assessments")
        else:
            self.logger.info(f"[Aggregator] Revising draft based on critiques (Revision mode)")
    
    def log_challenger(self, challenger_name: str, is_valid: bool, recommendation: str):
        """Log challenger critique"""
        status = "VALID" if is_valid else "INVALID"
        self.logger.info(
            f"[{challenger_name.upper()}] Status: {status}, "
            f"Recommendation: {recommendation.upper()}"
        )
    
    def log_verifier(self, needs_revision: bool, revision_count: int):
        """Log verifier decision"""
        if needs_revision:
            self.logger.info(
                f"[Verifier] Revision needed. Current revision count: {revision_count}"
            )
        else:
            self.logger.info(
                f"[Verifier] Assessment accepted. Total revisions: {revision_count}"
            )
    
    def log_final_result(self, result: Dict[str, Any]):
        """Log final assessment result"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("FINAL ASSESSMENT RESULT")
        self.logger.info("=" * 80)
        
        if result.get("synthesized_draft"):
            draft = result["synthesized_draft"]
            self.logger.info(f"Risk Score: {draft.score}/5")
            
            # Log dual-factor assessment if available
            if draft.risk_assessment:
                ra = draft.risk_assessment
                self.logger.info(f"Dual-Factor Assessment:")
                self.logger.info(f"  Frequency: {ra.frequency_score}/5 - {ra.frequency_rationale}")
                self.logger.info(f"  Impact: {ra.impact_score}/5 - {ra.impact_rationale}")
                self.logger.info(f"  Final Risk Score: {ra.final_risk_score}/25 ({ra.risk_classification})")
                self.logger.info(f"  Calculation: {ra.frequency_score} × {ra.impact_score} = {ra.final_risk_score}")
            
            self.logger.info(f"Summary: {draft.reasoning.summary}")
            self.logger.info(f"Key Arguments: {len(draft.reasoning.key_arguments)}")
            self.logger.info(
                f"Regulatory Citations: {len(draft.reasoning.regulatory_citations)}"
            )
            self.logger.info(f"Vulnerabilities: {len(draft.reasoning.vulnerabilities)}")
        
        self.logger.info(f"Total Revisions: {result.get('revision_count', 0)}")
        self.logger.info(f"Total Critiques: {len(result.get('critiques', []))}")
        
        # Log critique summary
        critiques = result.get("critiques", [])
        if critiques:
            self.logger.info("\nCritique Summary:")
            for critique in critiques:
                status = "✓" if critique.is_valid else "✗"
                self.logger.info(
                    f"  {status} {critique.challenger_name}: "
                    f"{critique.recommendation.upper()} "
                    f"(confidence: {critique.confidence:.1%})"
                )
                if critique.issues:
                    self.logger.info(f"    Issues: {len(critique.issues)}")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error"""
        if context:
            self.logger.error(f"[{context}] Error: {str(error)}")
        else:
            self.logger.error(f"Error: {str(error)}")
    
    def log_completion(self, filepath: Optional[str] = None):
        """Log workflow completion"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("WORKFLOW COMPLETED")
        if filepath:
            self.logger.info(f"Result saved to: {filepath}")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info("=" * 80 + "\n")
    
    def log_conversations(self, records: List[Dict[str, Any]], max_chars: int = 160):
        """Log per-message prompts/responses (compact)"""
        if not records:
            self.logger.info("No conversation records captured.")
            return
        self.logger.info("\nConversation Trace (all agents):")

        def _shorten(text: str) -> str:
            """Condense whitespace and truncate for neat logging."""
            if text is None:
                return ""
            compact = " ".join(text.split())
            return (compact[:max_chars] + "...") if len(compact) > max_chars else compact

        for idx, rec in enumerate(records, 1):
            prompt_snip = _shorten(rec.get("prompt", ""))
            resp_snip = _shorten(rec.get("response", ""))
            self.logger.info("----------------------------------------------------------------")
            self.logger.info(
                f"[{idx}] stage={rec.get('stage')} | role={rec.get('role')} | "
                f"model={rec.get('model')} | rev={rec.get('revision')}"
            )
            self.logger.info(f"  prompt: {prompt_snip}")
            self.logger.info(f"  resp:   {resp_snip}")
        self.logger.info(f"Total conversation entries: {len(records)}")
    
    def get_log_file_path(self) -> str:
        """Get path to current log file"""
        return str(self.log_file)

