"""
LangGraph Workflow - Complete Multi-Agent System Orchestration
Created: 2025-01-XX
"""

from langgraph.graph import StateGraph, END

from src.schemas import StateSchema
from src.agents.generator_ensemble import generator_ensemble_node
from src.agents.aggregator import aggregator_node
from src.agents.challenger_a import challenger_a_node
from src.agents.challenger_b import challenger_b_node
from src.agents.challenger_c import challenger_c_node
from src.agents.verifier import verifier_node, should_continue
from src.agents.escalation_node import escalation_node


def create_workflow():
    """Create and compile the LangGraph workflow"""
    
    # Create StateGraph
    workflow = StateGraph(StateSchema)
    
    # Add nodes
    workflow.add_node("generator_ensemble", generator_ensemble_node)
    workflow.add_node("aggregator", aggregator_node)
    workflow.add_node("challenger_a", challenger_a_node)
    workflow.add_node("challenger_b", challenger_b_node)
    workflow.add_node("challenger_c", challenger_c_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("escalation", escalation_node)
    
    # Define edges
    workflow.set_entry_point("generator_ensemble")
    
    # Generator -> Aggregator
    workflow.add_edge("generator_ensemble", "aggregator")
    
    # Aggregator -> All Challengers (parallel)
    workflow.add_edge("aggregator", "challenger_a")
    workflow.add_edge("aggregator", "challenger_b")
    workflow.add_edge("aggregator", "challenger_c")
    
    # All Challengers -> Verifier
    workflow.add_edge("challenger_a", "verifier")
    workflow.add_edge("challenger_b", "verifier")
    workflow.add_edge("challenger_c", "verifier")
    
    # Verifier -> Conditional routing
    workflow.add_conditional_edges(
        "verifier",
        should_continue,
        {
            "revise": "aggregator",  # Loop back to aggregator for revision
            "escalate": "escalation",  # Route to human escalation
            "end": END
        }
    )
    
    # Escalation -> End (human review required)
    workflow.add_edge("escalation", END)
    
    # Compile and return
    return workflow.compile()


# Create workflow instance
workflow = create_workflow()

