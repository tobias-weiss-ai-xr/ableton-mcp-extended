"""
Generate clips node - Create MIDI clips with music content.
"""
from typing import List, Dict, Any, Optional
import random
from agentic_mix.state import GraphState
from agentic_mix.tools import (
    create_clip, add_notes_to_clip, create_drum_pattern,
    generate_chord_progression_clip, generate_melody_clip
)
from agentic_mix.sound_sets import (
    track_name_by_index, GENRE_PATTERNS, PROGRESSIONS,
    DRUM_PATTERNS as _DRUM_PATTERNS_RAW,
    MINOR_SCALE as _MINOR_SCALE_CATALOG,
)


def generate_clips_node(state: GraphState) -> GraphState:
    """
    Generate clips for all tracks in the session.

    This node:
    1. Creates multiple clips per track (typically 8-12)
    2. Generates appropriate content per track type (drums, bass, chords, etc.)
    3. Adds variation to avoid repetitive patterns
    """
    config = state["config"]
    session_info = state["session_info"]
    track_indices = session_info["track_indices"]
    feedback = state["feedback"]

    feedback.append("Generating clips...")

    try:
        clips_per_track = 8  # Number of clip variations per track
        clip_length = config["section_duration_beats"]  # Beats per clip

        for track_idx, track_index in enumerate(track_indices):
            track_name = _get_track_name_by_index(track_idx, config["genre"], len(track_indices))

            # Generate clips for this track
            for clip_idx in range(clips_per_track):
                feedback.append(f"Generating clip {clip_idx + 1}/{clips_per_track} for {track_name}")

                def _check(resp, what):
                    """Surface command failures instead of silently dropping clips."""
                    if isinstance(resp, dict) and resp.get("status") == "error":
                        feedback.append(f"ERROR: {what} on {track_name} clip {clip_idx}: {resp.get('message', resp.get('error', '?'))}")

                if track_idx == 0 and "1" in track_name:
                    # Primary drums - use pattern templates with variation
                    pattern = _select_drums_pattern(config["genre"], clip_idx)
                    _check(create_drum_pattern(track_index, clip_idx,
                                     pattern_name=pattern,
                                     length=clip_length), "drum pattern")

                elif "Drums" in track_name and "1" not in track_name:
                    # Secondary drums/percussion
                    pattern = _select_drums_pattern(config["genre"], clip_idx)
                    _check(create_drum_pattern(track_index, clip_idx,
                                     pattern_name=pattern,
                                     length=clip_length), "drum pattern")

                elif "Bass" in track_name:
                    # Bass - simple root notes
                    notes = _generate_bass_pattern(config["key"], clip_idx, clip_length)
                    _check(create_clip(track_index, clip_idx, length=clip_length), "create clip")
                    _check(add_notes_to_clip(track_index, clip_idx, notes), "bass notes")

                elif "Chords" in track_name or "Synth" in track_name:
                    # Chords - use progression generator
                    progression = _select_progression(config["genre"], clip_idx)
                    _check(generate_chord_progression_clip(
                        track_index, clip_idx,
                        key=config["key"],
                        progression=progression,
                        duration_per_chord=clip_length / len(progression),
                        pattern_type="sustained"
                    ), "chord progression")

                elif "Pads" in track_name or "Atmosphere" in track_name:
                    # Pads/atmosphere - slow, sustained notes
                    notes = _generate_pad_notes(config["key"], clip_idx, clip_length)
                    _check(create_clip(track_index, clip_idx, length=clip_length), "create clip")
                    _check(add_notes_to_clip(track_index, clip_idx, notes), "pad notes")

                elif "FX" in track_name:
                    # FX - sporadic, rhythmic hits
                    notes = _generate_fx_pattern(clip_idx, clip_length)
                    _check(create_clip(track_index, clip_idx, length=clip_length), "create clip")
                    _check(add_notes_to_clip(track_index, clip_idx, notes), "fx notes")

                else:
                    # Melody/pads/etc
                    scale, complexity = _get_scale_settings(config["genre"], clip_idx)
                    _check(generate_melody_clip(
                        track_index, clip_idx,
                        key=config["key"],
                        scale=scale,
                        length_beats=clip_length,
                        complexity=complexity
                    ), "melody")

        feedback.append(f"Generated {clips_per_track * len(track_indices)} clips")

    except Exception as e:
        state["errors"].append(f"Clip generation failed: {str(e)}")
        feedback.append(f"ERROR: {state['errors'][-1]}")

    return state


def _get_track_name_by_index(idx: int, genre: str, total_tracks: int) -> str:
    """Helper to get track name from centralized sets."""
    return track_name_by_index(genre, idx, total_tracks)


def _select_drums_pattern(genre: str, clip_idx: int) -> str:
    """Select drum pattern with variation from central catalog."""
    patterns = GENRE_PATTERNS.get(genre, GENRE_PATTERNS["dub_techno"])
    return patterns[clip_idx % len(patterns)]


def _select_progression(genre: str, clip_idx: int) -> List[str]:
    """Select chord progression from central catalog."""
    idx = clip_idx % len(PROGRESSIONS)
    p = PROGRESSIONS[idx]
    # Convert uppercase major to lowercase minor notation (e.g. "I" -> "i")
    if genre in ("dub_techno", "ambient"):
        return [c.lower() for c in p]  # use minor notation for dub
    return p


def _generate_bass_pattern(key: str, clip_idx: int, length_beats: float) -> List[Dict[str, Any]]:
    """Generate bass note pattern."""
    # Key to root note mapping
    root_map = {"Fm": 41, "Cm": 48, "Am": 45, "Gm": 43, "Dm": 50}
    root = root_map.get(key, 41)

    notes = []
    bars = int(length_beats / 4)

    # Simple pattern with variation
    for bar in range(bars):
        note_beats = [bar * 4, bar * 4 + 2, bar * 4 + 3.5] if clip_idx % 2 == 0 else [bar * 4 + 1, bar * 4 + 3]

        for beat in note_beats:
            if beat < length_beats:
                notes.append({
                    "pitch": root,
                    "start_time": float(beat),
                    "duration": 0.5,
                    "velocity": 100 + random.randint(-10, 10),
                    "mute": False
                })

    return notes if notes else [{"pitch": root, "start_time": 0.0, "duration": 1.0, "velocity": 100, "mute": False}]


def _generate_pad_notes(key: str, clip_idx: int, length_beats: float) -> List[Dict[str, Any]]:
    """Generate pad/atmosphere notes."""
    # Minor chord notes for pads
    chord_variations = [
        [41, 44, 48],   # F minor
        [36, 39, 43],   # F minor oct down
        [53, 56, 60],   # F minor oct up
        [60, 63, 67],   # C minor
    ]

    chord = chord_variations[clip_idx % len(chord_variations)]
    notes = []

    # Slow, sustained pads
    num_chords = 4
    chord_len = length_beats / num_chords

    for i in range(num_chords):
        for note in chord:
            notes.append({
                "pitch": note + random.randint(-1, 1),
                "start_time": i * chord_len,
                "duration": chord_len - 0.5,
                "velocity": 70 + random.randint(-15, 15),
                "mute": False
            })

    return notes if notes else [{"pitch": 53, "start_time": 0.0, "duration": 2.0, "velocity": 70, "mute": False}]


def _generate_fx_pattern(clip_idx: int, length_beats: float) -> List[Dict[str, Any]]:
    """Generate sporadic FX hits."""
    notes = []
    num_hits = random.randint(2, 5)

    for i in range(num_hits):
        beat = random.uniform(0, length_beats - 2)
        notes.append({
            "pitch": random.randint(60, 80),
            "start_time": beat,
            "duration": 0.1,
            "velocity": random.randint(80, 127),
            "mute": False
        })

    notes.sort(key=lambda n: n["start_time"])
    return notes if notes else [{"pitch": 72, "start_time": 0.0, "duration": 0.1, "velocity": 100, "mute": False}]


def _get_scale_settings(genre: str, clip_idx: int) -> tuple:
    """Get scale and complexity for melody generation."""
    scales = ["minor", "dorian", "phrygian"]
    complexities = ["simple", "medium", "complex"]

    scale = scales[clip_idx % len(scales)]
    complexity = complexities[clip_idx % len(complexities)]

    return scale, complexity
