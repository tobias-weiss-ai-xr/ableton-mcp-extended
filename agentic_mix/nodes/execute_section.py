"""Execute section node - single section execution"""

import time
from typing import Any, Dict, Callable, Optional
import agentic_mix.tools as tools

TECHNIQUE_TO_NAME: Dict[str, str] = {
    "bass_forward": "apply_bass_forward_mix",
    "dub_drop": "apply_dub_drop",
    "crossfade": "apply_crossfade",
    "send_sweep": "apply_send_sweep",
    "strip_and_build": "apply_strip_and_build",
    "filter_sweep": "apply_filter_buildup",
    "volume_automation": "apply_volume_automation",
    "scene_transition": "apply_scene_transition",
}


def _resolve_technique_fn(technique: str) -> Optional[Callable]:
    """Resolve mixing technique name to callable function.

    Uses dynamic lookup so that tests can mock individual tool functions.
    """
    name = TECHNIQUE_TO_NAME.get(technique)
    if name is None:
        return None
    return getattr(tools, name, None)


def execute_section_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ONE section: trigger scene, apply technique, record metrics

    Args:
        state: GraphState dict containing current_section_index,
               arrangement list, client, and playback_metrics.

    Returns:
        Updated GraphState dict with transition recorded.
    """
    section_idx = state["current_section_index"]
    section = state["arrangement"][section_idx]
    client = state["client"]

    # Trigger the scene
    client.trigger_scene(section["scene_index"])
    time.sleep(0.5)  # Let Ableton transition settle

    # Apply mixing technique if specified
    technique = section.get("mixing_technique", "none")
    if technique != "none":
        fn = _resolve_technique_fn(technique)
        if fn is not None:
            fn(client, section)

    # Record section transition in metrics
    timestamp = time.time()
    state["playback_metrics"]["section_transitions"].append({
        "section_index": section_idx,
        "section_name": section["name"],
        "technique": technique,
        "start_time": timestamp,
        "scene_index": section["scene_index"],
    })

    return state
