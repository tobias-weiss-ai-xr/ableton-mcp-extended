"""Execute section node - single section execution"""

import time
from typing import Any, Dict

from agentic_mix.tools import trigger_scene
from agentic_mix.nodes.execute_mix_loop import apply_mixing_technique


def execute_section_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ONE section: trigger scene, apply technique, record metrics.

    Uses the tools module directly (global TCP client) instead of
    state["client"], matching setup_session and generate_clips pattern.

    Args:
        state: GraphState dict containing current_section_index,
               arrangement, track_states, and playback_metrics.

    Returns:
        Updated GraphState dict with transition recorded.
    """
    section_idx = state["current_section_index"]
    section = state["arrangement"][section_idx]
    track_indices = state["session_info"]["track_indices"]
    config = state["config"]

    # Trigger the scene
    scene_index = section["scene_index"]
    if scene_index is not None:
        trigger_scene(scene_index)
        time.sleep(0.5)  # Let Ableton transition settle

    # Apply mixing technique if specified (reuses execute_mix_loop's implementation)
    technique = section.get("mixing_technique", "none")
    if technique != "none":
        next_section = None
        if section_idx + 1 < len(state["arrangement"]):
            next_section = state["arrangement"][section_idx + 1]
        apply_mixing_technique(
            section=section,
            track_indices=track_indices,
            config=config,
            next_section=next_section,
        )

    # Record section transition in metrics
    timestamp = time.time()
    state["playback_metrics"]["section_transitions"].append({
        "section_index": section_idx,
        "section_name": section["name"],
        "technique": technique,
        "start_time": timestamp,
        "scene_index": scene_index,
        "energy_level": section["energy_level"],
    })

    return state
