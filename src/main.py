"""
Main Entry Point for Multi-Agent System
Created: 2025-01-XX
"""

from typing import Dict, Any, Optional
from tqdm import tqdm
from src.graph import workflow
from src.schemas import StateSchema
from src.config import Config
from src.utils.logger import AssessmentLogger
from src.utils.result_saver import save_result_to_json
from src.utils.conversation_recorder import start_run, end_run, get_records


def run_risk_assessment(
    risk_input: str,
    save_result: bool = True,
    enable_logging: bool = True,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run the complete risk assessment workflow
    
    Args:
        risk_input: Description of the IoT device scenario
        save_result: Whether to automatically save result to JSON file
        enable_logging: Whether to enable workflow logging
        
    Returns:
        Final state with synthesized_draft and critiques
    """
    # Initialize logger and conversation recorder
    logger = None
    start_run()
    if enable_logging:
        logger = AssessmentLogger()
        logger.log_start(risk_input)
    
    try:
        # Validate API keys
        missing_keys = Config.validate_api_keys()
        if missing_keys:
            error_msg = f"Missing required API keys: {', '.join(missing_keys)}"
            if logger:
                logger.log_error(ValueError(error_msg), "API Key Validation")
            raise ValueError(error_msg)
        
        # Initialize state
        initial_state: StateSchema = {
            "risk_input": risk_input,
            "draft_assessments": [],
            "synthesized_draft": None,
            "critiques": [],
            "revision_count": 0
        }
        
        # Run workflow with progress tracking
        print("\n🔄 Assessment for IoT Risk")
        print("Running Multi-Agent Workflow...\n")
        if logger:
            logger.logger.info("Starting workflow execution...")
        
        final_state = workflow.invoke(initial_state)
        print()  # New line after progress bars
        
        # Log final result
        if logger:
            logger.log_final_result(final_state)
            logger.log_conversations(get_records())
        
        # Save result to JSON file
        saved_filepath = None
        if save_result:
            try:
                saved_filepath = save_result_to_json(
                    final_state, risk_input, get_records(), output_dir=output_dir
                )
                print(f"💾 Assessment for IoT Risk - Result saved to: {saved_filepath}")
                if logger:
                    logger.logger.info(f"Result saved to JSON: {saved_filepath}")
            except Exception as e:
                error_msg = f"Failed to save result: {str(e)}"
                print(f"⚠️  {error_msg}")
                if logger:
                    logger.log_error(e, "Result Saving")
        
        # Log completion
        if logger:
            logger.log_completion(saved_filepath)
        
        return final_state
        
    except Exception as e:
        if logger:
            logger.log_error(e, "Workflow Execution")
            logger.log_completion()
        raise
    finally:
        end_run()


def run_risk_assessment_async(risk_input: str):
    """
    Run the complete risk assessment workflow asynchronously
    
    Args:
        risk_input: Description of the IoT device scenario
        
    Returns:
        Async generator yielding state updates
    """
    # Validate API keys
    missing_keys = Config.validate_api_keys()
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    # Initialize state
    initial_state: StateSchema = {
        "risk_input": risk_input,
        "draft_assessments": [],
        "synthesized_draft": None,
        "critiques": [],
        "revision_count": 0
    }
    
    # Stream workflow execution
    for state in workflow.stream(initial_state):
        yield state


if __name__ == "__main__":
    # Example usage
    example_input = """
    IoT Smart Thermostat Device:
    - Connects to home WiFi network
    - No encryption on firmware updates
    - Default admin password (admin/admin)
    - Collects user temperature preferences
    - No security update mechanism
    - PSTI Act 2022 compliance status unknown
    """
    
    print("Running risk assessment...")
    result = run_risk_assessment(example_input)
    
    print("\n=== Final Assessment ===")
    if result.get("synthesized_draft"):
        draft = result["synthesized_draft"]
        print(f"Score: {draft.score}/5")
        
        # Display dual-factor assessment if available
        if draft.risk_assessment:
            ra = draft.risk_assessment
            print(f"\n=== Dual-Factor Risk Assessment ===")
            print(f"Frequency Score: {ra.frequency_score}/5")
            print(f"Frequency Rationale: {ra.frequency_rationale}")
            print(f"Impact Score: {ra.impact_score}/5")
            print(f"Impact Rationale: {ra.impact_rationale}")
            print(f"Final Risk Score: {ra.final_risk_score}/25")
            print(f"Risk Classification: {ra.risk_classification}")
            print(f"Calculation: {ra.frequency_score} × {ra.impact_score} = {ra.final_risk_score}")
        
        print(f"\nSummary: {draft.reasoning.summary}")
        print(f"\nKey Arguments:")
        for arg in draft.reasoning.key_arguments:
            print(f"  - {arg}")
        print(f"\nRegulatory Citations: {', '.join(draft.reasoning.regulatory_citations)}")
        print(f"Vulnerabilities: {', '.join(draft.reasoning.vulnerabilities)}")
    
    print(f"\n=== Critiques ({len(result.get('critiques', []))}) ===")
    for critique in result.get("critiques", []):
        print(f"\n{critique.challenger_name}:")
        print(f"  Valid: {critique.is_valid}")
        print(f"  Confidence: {critique.confidence:.2%}")
        print(f"  Recommendation: {critique.recommendation}")
        if critique.issues:
            print(f"  Issues: {', '.join(critique.issues)}")
    
    print(f"\nRevision Count: {result.get('revision_count', 0)}")

