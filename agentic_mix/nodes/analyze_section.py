"""Analyze section node - audio capture + adaptation decision"""

import logging
from typing import Any, Dict

from agentic_mix.state import (
    AudioAnalysisData,
)
from agentic_mix.audio_capture import capture_audio_snapshot
from agentic_mix.adaptation_logic import (
    decide_adaptations,
    apply_adaptations_to_section,
    is_valid_snapshot,
)

logger = logging.getLogger(__name__)

DEFAULT_ANALYSIS: Dict[str, Any] = {
    "timestamp": 0.0,
    "bpm": None,
    "beat": None,
    "rms": 0.5,
    "loudness_lufs": -18.0,
    "key": None,
    "key_confidence": None,
    "spectral_centroid_hz": 5000.0,
    "spectral_rolloff_hz": 1000.0,
}


def analyze_section_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze audio output, decide on adaptation, store feedback

    Called after each execute_section. Captures audio from the current
    section's output, validates readings, and decides adaptations for
    the next section.

    Args:
        state: GraphState dict with current_section_index, arrangement,
               config, feedback, audio_snapshot, and errors.

    Returns:
        Updated GraphState dict with new feedback data.
    """
    section_idx = state["current_section_index"]
    section = state["arrangement"][section_idx]
    arrangement = state["arrangement"]

    try:
        # Capture current audio snapshot
        analysis_raw = capture_audio_snapshot(state["config"])
        analysis_data = AudioAnalysisData(**analysis_raw)  # type: ignore[arg-type]

        # Validate readings
        if not is_valid_snapshot(analysis_data):
            logger.warning(
                "Invalid audio snapshot for section %s: %s",
                section_idx,
                analysis_data,
            )
            state["errors"].append(
                f"analyze_section_node: invalid snapshot for section {section_idx}"
            )
            if state["feedback"]["history"]:
                last_valid = state["feedback"]["history"][-1][1]
                analysis_data = last_valid
            else:
                analysis_data = AudioAnalysisData(**DEFAULT_ANALYSIS)  # type: ignore[arg-type]

        state["audio_snapshot"] = analysis_data

        # Store in feedback history
        state["feedback"]["history"].append((section_idx, analysis_data))
        state["feedback"]["energy_trend"].append(analysis_data["rms"])

        # Analyze and adapt for NEXT section (if any)
        if section_idx < len(arrangement) - 1:
            next_section = arrangement[section_idx + 1]

            try:
                adaptations = decide_adaptations(
                    analysis_data, section, next_section, state["config"]
                )

                apply_adaptations_to_section(adaptations, next_section)

                for adapt in adaptations:
                    state["feedback"]["adaptations"].append(adapt)

                logger.info(
                    "Section %s \u2192 applied %s adaptations to section %s",
                    section_idx,
                    len(adaptations),
                    section_idx + 1,
                )

            except Exception as e:
                logger.error("Adaptation logic failed for section %s: %s", section_idx, e)
                state["feedback"]["adaptations"].append({  # type: ignore[typeddict-item]
                    "type": "error",
                    "target_section": section_idx + 1,
                    "value": 0.0,
                    "tracks": None,
                    "from_technique": None,
                    "to_technique": None,
                    "message": f"Failed to adapt: {e}",
                })
                state["errors"].append(f"analyze_section_node: {e}")

    except Exception as e:
        logger.error("Audio capture failed for section %s: %s", section_idx, e)
        state["errors"].append(f"analyze_section_node: {e}")
        state["audio_snapshot"] = None

    return state
