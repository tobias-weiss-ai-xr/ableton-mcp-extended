"""
Execute mix loop node - Run the live mix by triggering sections and applying mixing.
"""
from typing import Dict, Any
import time
from agentic_mix.state import GraphState
from agentic_mix.tools import (
    trigger_scene, start_playback, stop_playback,
    apply_bass_forward_mix, apply_dub_drop, apply_crossfade,
    apply_crossfader_sweep, apply_send_sweep, apply_strip_and_build,
    apply_filter_buildup, apply_volume_automation, batch_fire_clips
)


def execute_mix_loop_node(state: GraphState) -> GraphState:
    """
    Execute the live mix by triggering sections and applying mixing techniques.

    This node:
    1. Triggers each section sequentially
    2. Applies mixing techniques per section
    3. Handles transitions between sections
    4. Records metrics and feedback
    """
    config = state["config"]
    arrangement = state["arrangement"]
    track_indices = state["session_info"].track_indices
    feedback = state["feedback"]
    metrics = state["playback_metrics"]

    feedback.append("Starting mix execution...")
    print("=" * 60)
    print(f"Starting {config.duration_minutes}m mix ({config.genre}, {config.tempo} BPM)")
    print("=" * 60)

    try:
        # Start playback
        start_playback()
        metrics["start_time"] = time.time()

        # Execute each section
        for section_idx, section in enumerate(arrangement):
            feedback.append(f"Executing section {section_idx + 1}/{len(arrangement)}: {section.name}")

            # Fire scene/trigger section
            if section.scene_index is not None:
                trigger_section(section.scene_index, track_indices, section.tracks_active)

            # Apply mixing technique
            apply_mixing_technique(
                section=section,
                track_indices=track_indices,
                config=config,
                next_section=arrangement[section_idx + 1] if section_idx + 1 < len(arrangement) else None
            )

            # Record metrics
            metrics["section_transitions"].append({
                "section": section.name,
                "index": section_idx,
                "energy_level": section.energy_level,
                "technique": section.mixing_technique
            })

            # Wait for section duration
            section_duration_seconds = (section.end_beat - section.start_beat) * (60 / config.tempo)

            # Subtract current segment time from wait
            # Note: Mixing techniques include their own sleep/delays
            # So we wait for remaining time
            feedback.append(f"  Playing for {section_duration_seconds:.0f} seconds")
            time.sleep(max(0, section_duration_seconds - 5))  # Subtract ~5s for mixing actions

        # Stop playback
        stop_playback()
        metrics["current_time"] = time.time()
        duration = metrics["current_time"] - metrics["start_time"]
        feedback.append(f"Mix complete. Total duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print("=" * 60)
        print(f"Mix complete ({duration/60:.1f} minutes)")
        print("=" * 60)

        state["complete"] = True

    except KeyboardInterrupt:
        stop_playback()
        feedback.append("Mix interrupted by user")
        state["complete"] = False
    except Exception as e:
        stop_playback()
        state["error"] = f"Mix execution failed: {str(e)}"
        feedback.append(f"ERROR: {state['error']}")
        metrics["errors"].append(state["error"])

    return state


def trigger_section(scene_index: int, track_indices: list, active_tracks: list):
    """Trigger a scene by firing clips on active tracks."""
    try:
        # Fire the scene
        trigger_scene(scene_index)
        print(f"  Triggered scene {scene_index + 1}")
    except Exception as e:
        print(f"  Failed to trigger scene {scene_index}: {e}")


def apply_mixing_technique(section: any, track_indices: list, config: any, next_section: any = None):
    """Apply the mixing technique for a section."""
    technique = section.mixing_technique

    print(f"  Mixing technique: {technique}")

    try:
        if technique == "bass_forward" and len(track_indices) >= 3:
            # Boost bass, cut others
            bass_idx = track_indices[2]  # Assume bass at index 2
            other_tracks = [t for t in track_indices if t != bass_idx]
            apply_bass_forward_mix(bass_idx, other_tracks, bass_volume=0.85, other_volume=0.55)

        elif technique == "dub_drop":
            apply_dub_drop(
                track_indices=track_indices[:4],  # Drums + bass
                device_index=0,
                parameter_index=2,
                drop_value=0.2,
                return_value=0.75,
                drop_instant=True
            )

        elif technique == "crossfade" and next_section and len(track_indices) >= 2:
            # Crossfade between two tracks
            apply_crossfade(track_indices[0], track_indices[1], duration_beats=8, steps=8)

        elif technique == "send_sweep" and len(track_indices) > 0:
            # Sweep send amount
            apply_send_sweep(track_indices[0], send_index=0, from_amount=0.0, to_amount=0.6, duration_beats=8)

        elif technique == "strip_and_build":
            # Strip then rebuild
            apply_strip_and_build(
                track_indices=track_indices[:4],
                strip_volume=0.3,
                phase_beats=4.0
            )

        elif technique == "filter_sweep":
            # Filter buildup on active tracks
            apply_filter_buildup(
                track_indices=section.tracks_active[:4],
                device_index=0,
                parameter_index=2,
                start_value=0.3,
                end_value=0.8 + section.energy_level * 0.2,
                duration_beats=8,
                steps=8
            )

        elif technique == "volume_automation":
            # Volume curve
            curve = "rise" if section.energy_level > 0.5 else "fall"
            apply_volume_automation(
                track_indices=section.tracks_active,
                curve=curve,
                duration_beats=8,
                steps=8,
                min_volume=0.4,
                max_volume=0.9
            )

        elif technique == "scene_transition" and next_section:
            # Transition with wash
            if next_section.scene_index is not None:
                apply_scene_transition(next_section.scene_index, duration_beats=4, steps=4)

    except Exception as e:
        print(f"  Failed to apply {technique}: {e}")
