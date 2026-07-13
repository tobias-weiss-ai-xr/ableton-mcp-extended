"""
Main LangGraph workflow for the agentic mix pipeline.

Defines the graph structure with nodes and edges connecting them.
Audio feedback loop: execute_section -> analyze_section -> [loop|end]
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import (
    GraphState, Config, create_session_info, create_track_state,
    create_playback_metrics,
)
from .nodes.configure import configure_node
from .nodes.setup_session import setup_session_node
from .nodes.generate_clips import generate_clips_node
from .nodes.construct_arrangement import construct_arrangement_node
from .nodes.execute_section import execute_section_node
from .nodes.analyze_section import analyze_section_node


def more_sections(state: GraphState) -> str:
    """Conditional edge: loop back to execute_section if more sections remain.

    current_section_index is incremented by analyze_section_node after
    each section, so this checks if we still have sections to process:
    index < len(arrangement) means sections remain.

    Returns:
        "execute_section" if there are more sections to process,
        END otherwise.
    """
    current_idx = state["current_section_index"]
    if current_idx < len(state["arrangement"]):
        return "execute_section"
    return END


def create_mix_pipeline() -> StateGraph:
    """
    Create the LangGraph workflow for agentic Ableton mix generation.

    Graph structure with audio feedback loop:
    START -> configure -> setup_session -> generate_clips
         -> construct_arrangement
         -> execute_section -> analyze_section
         -> [more sections? -> execute_section, OR -> END]

    Each section is executed and analyzed in sequence, with audio analysis
    providing feedback to adapt the next section.
    """
    # Initialize the graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("configure", configure_node)
    workflow.add_node("setup_session", setup_session_node)
    workflow.add_node("generate_clips", generate_clips_node)
    workflow.add_node("construct_arrangement", construct_arrangement_node)
    workflow.add_node("execute_section", execute_section_node)
    workflow.add_node("analyze_section", analyze_section_node)

    # Define edges
    workflow.set_entry_point("configure")
    workflow.add_edge("configure", "setup_session")
    workflow.add_edge("setup_session", "generate_clips")
    workflow.add_edge("generate_clips", "construct_arrangement")
    workflow.add_edge("construct_arrangement", "execute_section")
    workflow.add_edge("execute_section", "analyze_section")

    # Conditional loop: analyze -> execute or end
    workflow.add_conditional_edges(
        "analyze_section",
        more_sections,
        {
            "execute_section": "execute_section",
            END: END,
        },
    )

    # Compile the graph
    # MemorySaver allows state persistence across runs
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app


def run_pipeline(config: Config) -> Dict[str, Any]:
    """
    Run the mix pipeline with the given configuration.

    Args:
        config: User configuration object

    Returns:
        Dictionary with pipeline state and feedback
    """
    # Initialize state with all required GraphState fields
    # NOTE: client must be injected before invoke() when using graph directly
    initial_state: GraphState = {
        "config": config,
        "session_info": create_session_info(),
        "arrangement": [],
        "track_states": [create_track_state() for _ in range(config["track_count"])],
        "playback_metrics": create_playback_metrics(),
        "feedback": {"history": [], "adaptations": [], "energy_trend": []},
        "errors": [],
        "complete": False,
        "current_section_index": 0,
        "audio_snapshot": None,
        "client": None,
    }

    # Create and run the pipeline
    app = create_mix_pipeline()

    # Run the graph
    final_state = app.invoke(initial_state)

    return {
        "state": final_state,
        "feedback": final_state["feedback"],
        "complete": final_state["complete"],
        "errors": final_state["errors"],
        "metrics": final_state["playback_metrics"],
    }
