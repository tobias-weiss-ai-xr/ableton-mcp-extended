"""
Configure node - Parse and validate user parameters for the mix pipeline.
"""
from agentic_mix.state import GraphState, Config


def _has_config_keys(config: object) -> bool:
    """Check if object has all required Config keys."""
    required = {"tempo", "duration_minutes", "genre", "track_count",
                "key", "energy_curve", "variation_level",
                "section_duration_beats"}
    return isinstance(config, dict) and required.issubset(config.keys())


def configure_node(state: GraphState) -> GraphState:
    """
    Initialize configuration from user parameters.

    This node parses the raw parameters and creates a Config object
    with validated values. It also logs the configuration for transparency.
    """
    config = state.get("config")

    # TypedDict can't use isinstance(), so check for key presence
    if not _has_config_keys(config):
        if isinstance(config, dict):
            config = Config(**config)
        else:
            config = Config()  # type: ignore[call-arg]

    # Validation (use dict access since Config is a TypedDict)
    if not (60 <= config["tempo"] <= 180):  # type: ignore[index]
        state["errors"].append(
            f"Tempo {config['tempo']} must be between 60 and 180 BPM"
        )
        return state

    if not (1 <= config["duration_minutes"] <= 480):  # type: ignore[index]
        state["errors"].append(
            f"Duration {config['duration_minutes']} min must be between 1 and 480"
        )
        return state

    if config["genre"] not in ["dub_techno", "house", "techno", "ambient"]:  # type: ignore[index]
        state["errors"].append(
            f"Genre {config['genre']} not supported"
        )
        return state

    if not (2 <= config["track_count"] <= 16):  # type: ignore[index]
        state["errors"].append(
            f"Track count {config['track_count']} must be between 2 and 16"
        )
        return state

    # Store validated config
    state["config"] = config  # type: ignore[typeddict-item]

    return state
