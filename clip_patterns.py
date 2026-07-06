"""
Clip pattern generation for dub techno MIDI clips.

Functions:
    - create_drum_pattern(track_idx, clip_idx, pattern_type, length)
    - create_bass_notes(track_idx, clip_idx, root, notes, duration)
    - create_pad_chords(track_idx, clip_idx, chords, voicing_type)

Pattern types one for drum patterns based on AGENTS.md:69-77:
    - one_drop: Classic dub techno (kick on 1, delayed snare)
    - rockers: Jamaican skank (kick/hat offbeat)
    - steppers: Even kick distribution
    - dub_techno: Syncopated dub

Usage:
    from clip_patterns import create_drum_pattern, create_bass_notes, create_pad_chords

    create_drum_pattern(0, 0, "one_drop", 4)
    create_bass_notes(1, 0, root=36, notes=[36, 39, 43, 48], duration=4)
"""

import logging
from typing import List, Dict, Any

from mcp_client import MCPClientTCP

logger = logging.getLogger(__name__)


# =============================================================================
# Drum Patterns (Task 4)
# =============================================================================

DRUM_PATTERNS = {
    "one_drop": {
        "description": "Classic dub techno - kick on beat 1, delayed snare on 3",
        "grid": "|X---|----|--X-|----|",
        "kick_note": 36,  # C2 - kick drum
        "snare_note": 40,  # E1 - snare/rim
        "hat_note": 42,   # F#1 - hi-hat
    },
    "rockers": {
        "description": "Jamaican skank - kick/hat offbeat emphasis",
        "grid": "|X-X-|---|X-X-|---|",
        "kick_note": 36,
        "snare_note": 40,
        "hat_note": 42,
    },
    "steppers": {
        "description": "Steppers rhythm - even kick distribution",
        "grid": "|X---|X---|X---|X---|",
        "kick_note": 36,
        "snare_note": 40,
        "hat_note": 42,
    },
    "dub_techno": {
        "description": "Syncopated dub - offbeat accents",
        "grid": "|X---|----|--X-|X---|",
        "kick_note": 36,
        "snare_note": 40,
        "hat_note": 42,
    },
}


def create_drum_pattern(
    track_idx: int,
    clip_idx: int,
    pattern_type: str = "one_drop",
    length: float = 4.0,
    velocity: int = 100
) -> Dict[str, Any]:
    """
    Create a drum pattern in the specified clip.

    Args:
        track_idx: Track index (0-based)
        clip_idx: Clip slot index (0-based)
        pattern_type: Pattern name (one_drop, rockers, steppers, dub_techno)
        length: Pattern length in beats (default 4 bars = 16 beats)
        velocity: Note velocity (0-127, default 100)

    Returns:
        Dictionary with creation result

    Raises:
        ValueError: If pattern_type is not recognized

    Note:
        Pattern grids from AGENTS.md:69-77:
        - one_drop = |X---|----|--X-|----| (kick on 1, snare on 3)
        - rockers = |X-X-|---|X-X-|---|
        - steppers = |X---|X---|X---|X---|
        - dub_techno = |X---|----|--X-|X---|
    """
    if pattern_type not in DRUM_PATTERNS:
        raise ValueError(f"Unknown pattern type: {pattern_type}. "
                       f"Available: {list(DRUM_PATTERNS.keys())}")

    pattern = DRUM_PATTERNS[pattern_type]
    client = MCPClientTCP()

    # Create clip
    try:
        result = client.send_command("create_clip", {
            "track_index": track_idx,
            "clip_index": clip_idx,
            "length": length
        })
        logger.info(f"Created clip at track {track_idx}, slot {clip_idx} with length {length}")
    except Exception as e:
        logger.warning(f"Failed to create clip: {e}")
        result = {"created": False}

    # Generate notes based on pattern
    notes = _generate_drum_notes(pattern_type, length, velocity)

    # Add notes to clip
    if notes:
        try:
            client.send_command("add_notes_to_clip", {
                "track_index": track_idx,
                "clip_index": clip_idx,
                "notes": notes
            })
            logger.info(f"Added {len(notes)} notes for {pattern_type} pattern")
        except Exception as e:
            logger.warning(f"Failed to add notes: {e}")

    return {
        "pattern_type": pattern_type,
        "notes_count": len(notes),
        "clip_created": result.get("created", False),
        "pattern": pattern
    }


def _generate_drum_notes(pattern_type: str, length: float, velocity: int) -> List[Dict[str, Any]]:
    """
    Generate MIDI notes for a drum pattern.

    Args:
        pattern_type: Pattern name
        length: Length in beats
        velocity: Note velocity

    Returns:
        List of note dictionaries: [{"pitch": int, "start_time": float,
                                    "duration": float, "velocity": int}]
    """
    pattern = DRUM_PATTERNS[pattern_type]
    notes = []
    kick_note = pattern["kick_note"]
    snare_note = pattern["snare_note"]
    hat_note = pattern["hat_note"]

    # Parse pattern grid to determine where to place notes
    # Grid pattern: |X---|----|--X-|----|
    # Each position is a 16th note (0.25 beats)
    if pattern_type == "one_drop":
        # Kick on beat 1, snare on beat 3
        notes.append({
            "pitch": kick_note,
            "start_time": 0.0,
            "duration": 0.5,
            "velocity": velocity
        })
        notes.append({
            "pitch": kick_note,
            "start_time": 4.0,
            "duration": 0.5,
            "velocity": int(velocity * 0.8)
        })
        notes.append({
            "pitch": snare_note,
            "start_time": 2.5,  # Dub delayed snare
            "duration": 0.5,
            "velocity": int(velocity * 0.9)
        })
        notes.append({
            "pitch": snare_note,
            "start_time": 6.5,
            "duration": 0.5,
            "velocity": int(velocity * 0.8)
        })

        # Add sparse hi-hats
        for i in range(0, int(length), 1.0):
            notes.append({
                "pitch": hat_note,
                "start_time": i,
                "duration": 0.25,
                "velocity": int(velocity * 0.6)
            })

    elif pattern_type == "rockers":
        # Offbeat kick pattern
        for i in range(0, int(length), 2.0):
            notes.append({
                "pitch": kick_note,
                "start_time": i,
                "duration": 0.5,
                "velocity": velocity
            })
            notes.append({
                "pitch": kick_note,
                "start_time": i + 0.5,
                "duration": 0.25,
                "velocity": int(velocity * 0.7)
            })
            # Hi-hats on offbeats
            notes.append({
                "pitch": hat_note,
                "start_time": i + 1.0,
                "duration": 0.25,
                "velocity": int(velocity * 0.6)
            })

    elif pattern_type == "steppers":
        # Even kick distribution
        for i in range(0, int(length), 1.0):
            notes.append({
                "pitch": kick_note,
                "start_time": i,
                "duration": 0.5,
                "velocity": velocity
            })
            # Snare on 2 and 4
            if i % 2 != 0:
                notes.append({
                    "pitch": snare_note,
                    "start_time": i,
                    "duration": 0.25,
                    "velocity": int(velocity * 0.8)
                })
            # Hi-hats every 0.5 beats
            notes.append({
                "pitch": hat_note,
                "start_time": i + 0.5,
                "duration": 0.125,
                "velocity": int(velocity * 0.5)
            })

    elif pattern_type == "dub_techno":
        # Syncopated dub pattern
        notes.append({
            "pitch": kick_note,
            "start_time": 0.0,
            "duration": 1.0,
            "velocity": velocity
        })
        notes.append({
            "pitch": snare_note,
            "start_time": 2.5,
            "duration": 0.5,
            "velocity": int(velocity * 0.9)
        })
        notes.append({
            "pitch": kick_note,
            "start_time": 3.0,
            "duration": 1.0,
            "velocity": int(velocity * 0.8)
        })
        # Add sparse hats on offbeats
        for i in range(0, int(length), 0.5):
            if i % 1.0 == 0.5:
                notes.append({
                    "pitch": hat_note,
                    "start_time": i,
                    "duration": 0.125,
                    "velocity": int(velocity * 0.5)
                })

    return notes


# =============================================================================
# Bass Patterns (Task 4)
# =============================================================================

# F minor scale notes (Fm for dub techno)
F_MINOR_SCALE = [36, 39, 43, 48, 51, 55, 60, 63]  # F, G#, Bb, C, D, F, G, Bb


def create_bass_notes(
    track_idx: int,
    clip_idx: int,
    root: int = 36,
    notes: List[int] = None,
    duration: float = 4.0,
    velocity: int = 110
) -> Dict[str, Any]:
    """
    Create bass notes in the specified clip.

    Args:
        track_idx: Track index (0-based)
        clip_idx: Clip slot index (0-based)
        root: Root MIDI note (default 36 = F2, F minor)
        notes: List of notes to create (default F minor triad)
        duration: Note duration in beats
        velocity: Note velocity (0-127, default 110 for bass)

    Returns:
        Dictionary with creation result

    Note:
        F minor scale notes: F-36, G#-39, Bb-43, C-48, D-51, F-55
        Default F minor triad: [36, 39, 43, 48]
    """
    if notes is None:
        # Default to F minor triad
        notes = [36, 39, 43, 48]

    client = MCPClientTCP()

    # Create clip
    try:
        result = client.send_command("create_clip", {
            "track_index": track_idx,
            "clip_index": clip_idx,
            "length": duration
        })
        logger.info(f"Created bass clip at track {track_idx}, slot {clip_idx}")
    except Exception as e:
        logger.warning(f"Failed to create bass clip: {e}")
        result = {"created": False}

    # Generate bass notes
    midi_notes = []
    for i, note in enumerate(notes):
        midi_notes.append({
            "pitch": note,
            "start_time": (duration / len(notes)) * i,
            "duration": duration / len(notes),
            "velocity": velocity
        })

    # Add notes to clip
    if midi_notes:
        try:
            client.send_command("add_notes_to_clip", {
                "track_index": track_idx,
                "clip_index": clip_idx,
                "notes": midi_notes
            })
            logger.info(f"Added {len(midi_notes)} bass notes: {notes}")
        except Exception as e:
            logger.warning(f"Failed to add bass notes: {e}")

    return {
        "notes": notes,
        "notes_count": len(midi_notes),
        "clip_created": result.get("created", False)
    }


# =============================================================================
# Pad Chords (Task 4)
# =============================================================================

# Common chord types with intervals from root
CHORD_INTERVALS = {
    "major": [0, 4, 7],          # Major triad
    "minor": [0, 3, 7],          # Minor triad
    "maj7": [0, 4, 7, 11],       # Major 7th
    "min7": [0, 3, 7, 10],       # Minor 7th
    "dom7": [0, 4, 7, 10],       # Dominant 7th
    "dim": [0, 3, 6],            # Diminished
    "sus2": [0, 2, 7],           # Suspended 2nd
    "sus4": [0, 5, 7],           # Suspended 4th
}


def create_pad_chords(
    track_idx: int,
    clip_idx: int,
    chords: List[List[int]],
    voicing_type: str = "close",
    duration_per_chord: float = 4.0,
    velocity: int = 85
) -> Dict[str, Any]:
    """
    Create pad chords in the specified clip.

    Args:
        track_idx: Track index (0-based)
        clip_idx: Clip slot index (0-based)
        chords: List of chord note arrays (e.g., [[60, 63, 67], [53, 56, 60]])
        voicing_type: Voicing type (close, open, drop2) - for future expansion
        duration_per_chord: Duration for each chord in beats
        velocity: Note velocity (0-127, default 85 for pads)

    Returns:
        Dictionary with creation result

    Note:
        Pad chords are typically held notes with longer durations.
        Example chords for C minor: [60, 63, 67] and [53, 56, 60]
    """
    client = MCPClientTCP()

    # Create clip (length = chords * duration_per_chord)
    total_length = len(chords) * duration_per_chord
    try:
        result = client.send_command("create_clip", {
            "track_index": track_idx,
            "clip_index": clip_idx,
            "length": total_length
        })
        logger.info(f"Created pad clip at track {track_idx}, slot {clip_idx}")
    except Exception as e:
        logger.warning(f"Failed to create pad clip: {e}")
        result = {"created": False}

    # Generate chord notes
    midi_notes = []
    for chord_idx, chord in enumerate(chords):
        start_time = chord_idx * duration_per_chord
        for note in chord:
            midi_notes.append({
                "pitch": note,
                "start_time": start_time,
                "duration": duration_per_chord,  # Hold for full chord duration
                "velocity": velocity
            })

    # Add notes to clip
    if midi_notes:
        try:
            client.send_command("add_notes_to_clip", {
                "track_index": track_idx,
                "clip_index": clip_idx,
                "notes": midi_notes
            })
            logger.info(f"Added {len(midi_notes)} pad notes ({len(chords)} chords)")
        except Exception as e:
            logger.warning(f"Failed to add pad notes: {e}")

    return {
        "chords_count": len(chords),
        "notes_count": len(midi_notes),
        "voicing_type": voicing_type,
        "clip_created": result.get("created", False)
    }


def build_chord(root: int, chord_type: str = "minor") -> List[int]:
    """
    Build a chord from root note and type.

    Args:
        root: Root MIDI note
        chord_type: Chord type (major, minor, maj7, min7, dom7, dim, sus2, sus4)

    Returns:
        List of MIDI notes for the chord

    Example:
        build_chord(60, "min7") → [60, 63, 67, 70]  # C minor 7th
    """
    if chord_type not in CHORD_INTERVALS:
        raise ValueError(f"Unknown chord type: {chord_type}")

    intervals = CHORD_INTERVALS[chord_type]
    return [root + interval for interval in intervals]