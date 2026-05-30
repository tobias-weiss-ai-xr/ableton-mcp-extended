"""
Main LangGraph workflow for the agentic mix pipeline.

Defines the graph structure with nodes and edges connecting them.
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import GraphState, Config, SessionInfo, TrackState, PlaybackMetrics
from .nodes.configure import configure_node
from .nodes.setup_session import setup_session_node
from .nodes.generate_clips import generate_clips_node
from .nodes.construct_arrangement import construct_arrangement_node
from .nodes.execute_mix_loop import execute_mix_loop_node
from .nodes.analyze_adapt import analyze_and_adapt_node


def create_mix_pipeline() -> StateGraph:
    """
    Create the LangGraph workflow for agentic Ableton mix generation.

    Graph structure:
    START → configure → setup_session → generate_clips → construct_arrangement
          → execute_mix_loop → analyze_adapt → END

    Each node processes the GraphState and passes it to the next node.
    Conditional edges can be added for branching logic.
    """
    # Initialize the graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("configure", configure_node)
    workflow.add_node("setup_session", setup_session_node)
    workflow.add_node("generate_clips", generate_clips_node)
    workflow.add_node("construct_arrangement", construct_arrangement_node)
    workflow.add_node("execute_mix_loop", execute_mix_loop_node)
    workflow.add_node("analyze_adapt", analyze_and_adapt_node)

    # Define edges
    workflow.set_entry_point("configure")
    workflow.add_edge("configure", "setup_session")
    workflow.add_edge("setup_session", "generate_clips")
    workflow.add_edge("generate_clips", "construct_arrangement")
    workflow.add_edge("construct_arrangement", "execute_mix_loop")
    workflow.add_edge("execute_mix_loop", "analyze_adapt")
    workflow.add_edge("analyze_adapt", END)

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
    # Initialize state
    initial_state: GraphState = {
        "config": config,
        "session_info": SessionInfo(),
        "arrangement": [],
        "current_section": 0,
        "track_states": [TrackState() for _ in range(config.track_count)],
        "playback_metrics": PlaybackMetrics(),
        "feedback": [],
        "complete": False,
        "error": None
    }

    # Create and run the pipeline
    app = create_mix_pipeline()

    # Run the graph
    final_state = app.invoke(initial_state)

    return {
        "state": final_state,
        "feedback": final_state["feedback"],
        "complete": final_state["complete"],
        "error": final_state["error"],
        "metrics": final_state["playback_metrics"]
    }
