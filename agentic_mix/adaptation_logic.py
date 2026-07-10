"""Adaptation logic for audio feedback loop"""

import logging
from typing import Any, Dict, List, Optional

from agentic_mix.state import (
    AudioAnalysisData,
    Adaptation,
)

logger = logging.getLogger(__name__)

VALID_TECHNIQUES = [
    "bass_forward", "dub_drop", "crossfade", "send_sweep",
    "strip_and_build", "filter_sweep", "volume_automation", "scene_transition", "none",
]


def decide_adaptations(
    current_analysis: AudioAnalysisData,
    current_section: Dict[str, Any],
    next_section: Dict[str, Any],
    config: Dict[str, Any],
) -> List[Adaptation]:
    """Analyze current section readings, return adaptations for next section

    Args:
        current_analysis: Audio readings from current section.
        current_section: Section dict (index, energy_level, mixing_technique, etc.).
        next_section: Section dict to be modified.
        config: Global configuration dict.

    Returns:
        List of Adaptation dicts to apply to next section.
    """
    adaptations: List[Adaptation] = []

    # Rule 1: Energy feedback
    if current_analysis["rms"] < 0.3:
        adaptations.append({
            "type": "energy_boost",
            "target_section": next_section["index"],
            "value": 0.15,
            "tracks": None,
            "from_technique": None,
            "to_technique": None,
        })
        logger.info(
            "Low energy detected (RMS=%.2f), boosting next section",
            current_analysis["rms"],
        )

    elif current_analysis["rms"] > 0.9:
        adaptations.append({
            "type": "energy_reduct",
            "target_section": next_section["index"],
            "value": -0.15,
            "tracks": None,
            "from_technique": None,
            "to_technique": None,
        })
        logger.warning(
            "High energy detected (RMS=%.2f), reducing next section",
            current_analysis["rms"],
        )

    # Rule 2: Spectral balance
    rolloff = current_analysis.get("spectral_rolloff_hz", 1.0) or 1.0
    spectral_ratio = current_analysis.get("spectral_centroid_hz", 5000.0) / rolloff

    if spectral_ratio > 0.8:
        adaptations.append({
            "type": "filter_adjust_down",
            "target_section": next_section["index"],
            "value": -0.1,
            "tracks": [0, 1, 2],
            "from_technique": None,
            "to_technique": None,
        })
        logger.info("Bright spectrum (ratio=%.2f), cutting highs", spectral_ratio)

    elif spectral_ratio < 0.3:
        adaptations.append({
            "type": "filter_adjust_up",
            "target_section": next_section["index"],
            "value": 0.1,
            "tracks": [0, 1, 2],
            "from_technique": None,
            "to_technique": None,
        })
        logger.info("Dark spectrum (ratio=%.2f), boosting mid/highs", spectral_ratio)

    # Rule 3: Technique feedback (clipping risk)
    if current_analysis["rms"] > 0.95:
        current_technique = current_section.get("mixing_technique", "none")
        safer_technique = "volume_automation"

        if current_technique != safer_technique:
            adaptations.append({
                "type": "technique_change",
                "target_section": next_section["index"],
                "value": 0.0,
                "tracks": None,
                "from_technique": current_technique,
                "to_technique": safer_technique,
            })
            logger.warning(
                "Clipping risk detected (RMS=%.2f), switching %s \u2192 %s",
                current_analysis["rms"],
                current_technique,
                safer_technique,
            )

    return adaptations


def apply_adaptations_to_section(
    adaptations: List[Adaptation],
    section: Dict[str, Any],
) -> None:
    """Apply adaptation list to a section (modifies in-place)

    Args:
        adaptations: List of Adaptation dicts to apply.
        section: Section dict to modify (will be mutated).
    """
    for adapt in adaptations:
        if adapt["type"] == "energy_boost":
            current_energy = section.get("energy_level", 5.0)
            new_energy = min(10.0, current_energy + adapt["value"])
            section["energy_level"] = new_energy

        elif adapt["type"] == "energy_reduct":
            current_energy = section.get("energy_level", 5.0)
            new_energy = max(0.0, current_energy + adapt["value"])
            section["energy_level"] = new_energy

        elif adapt["type"] == "filter_adjust_down":
            section["_filter_adjust"] = adapt.get("value", -0.1)
            section["_filter_tracks"] = adapt.get("tracks", [])

        elif adapt["type"] == "filter_adjust_up":
            section["_filter_adjust"] = adapt.get("value", 0.1)
            section["_filter_tracks"] = adapt.get("tracks", [])

        elif adapt["type"] == "technique_change":
            to_technique = adapt.get("to_technique")
            if to_technique is not None:
                section["mixing_technique"] = to_technique


def is_valid_snapshot(snapshot: AudioAnalysisData) -> bool:
    """Validate audio readings are sensible

    Checks for all-zero readings, out-of-range RMS, and clears
    low-confidence key readings.

    Args:
        snapshot: AudioAnalysisData to validate (may be mutated in-place
                  to clear low-confidence key).

    Returns:
        True if snapshot data is usable, False if readings are invalid.
    """
    # Skip if all readings are zero
    all_zero = all(
        v == 0 or v is None
        for v in snapshot.values()
        if not isinstance(v, str)
    )
    if all_zero:
        return False

    # Key readings only if confident
    key_confidence = snapshot.get("key_confidence")
    if key_confidence is not None and key_confidence < 0.5:
        snapshot["key"] = None

    # RMS must be in reasonable range
    rms = snapshot.get("rms", 0.0)
    if not (0.0 <= rms <= 1.0):
        return False

    # Spectral values must be positive
    if snapshot.get("spectral_centroid_hz", 0) <= 0:
        return False
    if snapshot.get("spectral_rolloff_hz", 0) <= 0:
        return False

    return True
