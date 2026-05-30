"""
Configure node - Parse and validate user parameters for the mix pipeline.
"""
from typing import Dict, Any
from agentic_mix.state import GraphState, Config


def configure_node(state: GraphState) -> GraphState:
    """
    Initialize configuration from user parameters.

    This node parses the raw parameters and creates a Config object
    with validated values. It also logs the configuration for transparency.
    """
    config = state.get("config")

    if not isinstance(config, Config):
        # Convert dict to Config if needed
        if isinstance(config, dict):
            config = Config(**config)
        else:
            # Default configuration
            config = Config()

    # Validation
    if not (60 <= config.tempo <= 180):
        state["error"] = f"Tempo {config.tempo} must be between 60 and 180 BPM"
        return state

    if not (1 <= config.duration_minutes <= 480):
        state["error"] = f"Duration {config.duration_minutes} min must be between 1 and 480"
        return state

    if config.genre not in ["dub_techno", "house", "techno", "ambient"]:
        state["error"] = f"Genre {config.genre} not supported"
        return state

    if not (2 <= config.track_count <= 16):
        state["error"] = f"Track count {config.track_count} must be between 2 and 16"
        return state

    # Log configuration
    feedback = f"""Configuration set:
    - Genre: {config.genre}
    - Tempo: {config.tempo} BPM
    - Duration: {config.duration_minutes} minutes
    - Track count: {config.track_count}
    - Key: {config.key}
    - Energy curve: {config.energy_curve}
    - Variation level: {config.variation_level}"""

    state["feedback"].append(feedback)
    state["config"] = config

    return state
