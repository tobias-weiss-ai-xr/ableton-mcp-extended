"""
Construct arrangement node - Build the section structure for the mix.
"""
from typing import List, Dict, Any
import random
from agentic_mix.state import GraphState, Section


def construct_arrangement_node(state: GraphState) -> GraphState:
    """
    Build the arrangement structure for the mix.

    This node AI-decides:
    1. Number of sections (based on duration)
    2. Section types and order
    3. Section energy levels (following energy_curve config)
    4. Which tracks are active per section
    5. Mixing techniques for transitions
    """
    config = state["config"]
    track_indices = state["session_info"].track_indices
    feedback = state["feedback"]

    feedback.append("Building arrangement structure...")

    try:
        # Calculate number of sections
        beats_per_section = config.section_duration_beats
        total_beats = config.duration_minutes * (config.tempo / 60)
        num_sections = int(total_beats / beats_per_section)

        feedback.append(f"Planning {num_sections} sections ({config.duration_minutes} minutes)")

        # Build sections
        arrangement = []
        current_beat = 0.0

        for section_idx in range(num_sections):
            section = _create_section(
                section_idx=section_idx,
                config=config,
                total_sections=num_sections,
                current_beat=current_beat,
                track_indices=track_indices
            )
            arrangement.append(section)
            current_beat += beats_per_section

            feedback.append(f"Section {section_idx + 1}: {section.name} (energy: {section.energy_level:.2f})")

        # Create scenes in Ableton
        from agentic_mix.tools import create_scene, set_scene_name

        scene_indices = []
        for section in arrangement:
            result = create_scene(index=section.index)
            scene_idx = result.get("scene_index", section.index)
            set_scene_name(scene_idx, section.name)
            section.scene_index = scene_idx
            scene_indices.append(scene_idx)

        # Update session info with scene indices
        state["session_info"].scene_indices = scene_indices
        state["arrangement"] = arrangement
        state["current_section"] = 0

        feedback.append(f"Arrangement created with {len(arrangement)} sections")

    except Exception as e:
        state["error"] = f"Arrangement construction failed: {str(e)}"
        feedback.append(f"ERROR: {state['error']}")

    return state


def _create_section(section_idx: int, config: any, total_sections: int,
                   current_beat: float, track_indices: List[int]) -> Section:
    """Create a single section with AI decisions."""
    # Section type based on position in arrangement
    section_type = _determine_section_type(section_idx, total_sections)

    # Energy level based on config.energy_curve
    energy_level = _calculate_energy_level(section_idx, total_sections, config.energy_curve)

    # Section name
    name = f"{section_type}_{section_idx + 1}"

    # Determine active tracks based on section type
    active_tracks = _get_active_tracks_for_section(section_type, track_indices)

    # Mixing technique for transition to next section
    mixing_technique = _select_mixing_technique(section_idx, total_sections, config.genre)

    return Section(
        index=section_idx,
        name=name,
        start_beat=current_beat,
        end_beat=current_beat + config.section_duration_beats,
        energy_level=energy_level,
        tracks_active=active_tracks,
        mixing_technique=mixing_technique,
        scene_index=None  # Set later
    )


def _determine_section_type(section_idx: int, total_sections: int) -> str:
    """Determine section type based on position."""
    if section_idx == 0:
        return "intro"
    elif section_idx < total_sections * 0.2:
        return "groove_a"
    elif section_idx < total_sections * 0.35:
        return "build"
    elif section_idx < total_sections * 0.45:
        return "drop"
    elif section_idx < total_sections * 0.55:
        return "groove_b"
    elif section_idx < total_sections * 0.7:
        return "breakdown"
    elif section_idx < total_sections * 0.85:
        return "groove_c"
    elif section_idx < total_sections * 0.95:
        return "build_2"
    else:
        return "outro"


def _calculate_energy_level(section_idx: int, total_sections: int,
                           energy_curve: str) -> float:
    """Calculate energy level for section."""
    progress = section_idx / max(1, total_sections - 1)

    if energy_curve == "gradual":
        # Gentle rise and fall
        if progress < 0.5:
            return 0.3 + (progress * 0.6)  # 0.3 -> 0.6
        else:
            return 0.6 - ((progress - 0.5) * 0.4)  # 0.6 -> 0.4

    elif energy_curve == "aggressive":
        # Peaks in middle
        return 1.0 - abs(progress - 0.5) * 1.5  # Peak at 0.5

    elif energy_curve == "gentle":
        # Overall low energy
        return 0.3 + (0.2 * random.random())

    else:  # "gradual" default
        return 0.4 + (0.4 * progress) if progress < 0.7 else 0.8 - (0.4 * (progress - 0.7))


def _get_active_tracks_for_section(section_type: str, track_indices: List[int]) -> List[int]:
    """Determine which tracks are active for a section type."""
    if section_type == "intro":
        # Minimal - bass, pads only
        return track_indices[2:4]  # Assume bass, chords at indices 2,3
    elif section_type == "groove_a":
        # Full mix
        return track_indices[:]
    elif section_type == "build":
        # Build up drums
        return track_indices[:]
    elif section_type == "drop":
        # Full energy
        return track_indices[:]
    elif section_type == "groove_b":
        return track_indices[:]
    elif section_type == "breakdown":
        # Strip down
        return track_indices[:4]  # Fewer tracks
    elif section_type == "outro":
        # Fade out
        return track_indices[:3]
    else:
        return track_indices[:]


def _select_mixing_technique(section_idx: int, total_sections: int, genre: str) -> str:
    """Select mixing technique for section transition."""
    techniques = [
        "scene_transition",
        "bass_forward",
        "dub_drop",
        "crossfade",
        "send_sweep",
        "strip_and_build",
        "filter_sweep",
        "volume_automation"
    ]

    # Vary techniques throughout arrangement
    return techniques[section_idx % len(techniques)]
