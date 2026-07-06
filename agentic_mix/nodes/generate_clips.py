"""
Generate clips node - Create MIDI clips with music content.
"""
from typing import List, Dict, Any
import random
from agentic_mix.state import GraphState
from agentic_mix.tools import (
    create_clip, add_notes_to_clip, create_drum_pattern,
    generate_chord_progression_clip, generate_melody_clip
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
    track_indices = session_info.track_indices
    feedback = state["feedback"]

    feedback.append("Generating clips...")

    try:
        clips_per_track = 8  # Number of clip variations per track
        clip_length = config.section_duration_beats  # Beats per clip

        for track_idx, track_index in enumerate(track_indices):
            track_name = _get_track_name_by_index(track_idx, config.genre, len(track_indices))

            # Generate clips for this track
            for clip_idx in range(clips_per_track):
                feedback.append(f"Generating clip {clip_idx + 1}/{clips_per_track} for {track_name}")

                if track_idx == 0 and "1" in track_name:
                    # Primary drums - use pattern templates with variation
                    pattern = _select_drums_pattern(config.genre, clip_idx)
                    create_drum_pattern(track_index, clip_idx,
                                     pattern_name=pattern,
                                     length=clip_length)

                elif "Drums" in track_name and "1" not in track_name:
                    # Secondary drums/percussion
                    pattern = _select_drums_pattern(config.genre, clip_idx)
                    create_drum_pattern(track_index, clip_idx,
                                     pattern_name=pattern,
                                     length=clip_length)

                elif "Bass" in track_name:
                    # Bass - simple root notes
                    notes = _generate_bass_pattern(config.key, clip_idx, clip_length)
                    create_clip(track_index, clip_idx, length=clip_length)
                    add_notes_to_clip(track_index, clip_idx, notes)

                elif "Chords" in track_name or "Synth" in track_name:
                    # Chords - use progression generator
                    progression = _select_progression(config.genre, clip_idx)
                    generate_chord_progression_clip(
                        track_index, clip_idx,
                        key=config.key,
                        progression=progression,
                        duration_per_chord=clip_length / len(progression),
                        pattern_type="sustained"
                    )

                elif "Pads" in track_name or "Atmosphere" in track_name:
                    # Pads/atmosphere - slow, sustained notes
                    notes = _generate_pad_notes(config.key, clip_idx, clip_length)
                    create_clip(track_index, clip_idx, length=clip_length)
                    add_notes_to_clip(track_index, clip_idx, notes)

                elif "FX" in track_name:
                    # FX - sporadic, rhythmic hits
                    notes = _generate_fx_pattern(clip_idx, clip_length)
                    create_clip(track_index, clip_idx, length=clip_length)
                    add_notes_to_clip(track_index, clip_idx, notes)

                else:
                    # Melody/pads/etc
                    scale, complexity = _get_scale_settings(config.genre, clip_idx)
                    generate_melody_clip(
                        track_index, clip_idx,
                        key=config.key,
                        scale=scale,
                        length_beats=clip_length,
                        complexity=complexity
                    )

        feedback.append(f"Generated {clips_per_track * len(track_indices)} clips")

    except Exception as e:
        state["error"] = f"Clip generation failed: {str(e)}"
        feedback.append(f"ERROR: {state['error']}")

    return state


def _get_track_name_by_index(idx: int, genre: str, total_tracks: int) -> str:
    """Helper to get track name."""
    track_templates = {
        "dub_techno": ["Drums 1", "Drums 2", "Bass", "Chords", "Pads", "FX", "Atmosphere", "Percussion"],
        "house": ["Drums", "Bass", "Chords", "Pads", "Vocals", "FX", "Atmosphere", "Percussion"],
        "techno": ["Drums", "Bass", "Synth 1", "Synth 2", "Atmosphere", "FX", "Pads", "Percussion"],
        "ambient": ["Pads", "Bass", "Atmosphere", "FX", "Percussion", "Texture", "Drone", "Reverbed"],
    }
    templates = track_templates.get(genre, track_templates["dub_techno"])
    return templates[idx] if idx < len(templates) else f"Track {idx + 1}"


def _select_drums_pattern(genre: str, clip_idx: int) -> str:
    """Select drum pattern with variation."""
    dub_patterns = ["one_drop", "rockers", "steppers", "dub_techno"]
    house_patterns = ["house_basic", "techno_4x4"]
    techno_patterns = ["techno_4x4"]
    ambient_patterns = ["one_drop"]

    if genre == "dub_techno":
        return dub_patterns[clip_idx % len(dub_patterns)]
    elif genre == "house":
        return house_patterns[clip_idx % len(house_patterns)]
    elif genre == "techno":
        return techno_patterns[clip_idx % len(techno_patterns)]
    else:
        return ambient_patterns[clip_idx % len(ambient_patterns)]


def _select_progression(genre: str, clip_idx: int) -> List[str]:
    """Select chord progression."""
    progressions = [
        ["i", "vii", "VI", "vii"],  # Classic dub
        ["i", "VII", "VI", "VII"],  # Minor progression
        ["i", "iv", "VII", "i"],    # Modal
        ["i", "VI", "VII", "v"],    # Tension
        ["i", "v", "VI", "VII"],    # Movement
        ["I", "V", "vi", "IV"],     # Major
    ]
    return progressions[clip_idx % len(progressions)]


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
