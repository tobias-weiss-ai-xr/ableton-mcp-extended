"""Chord namer and builder utilities."""

# MIDI note to note name mapping. Index = MIDI note % 12
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Chord quality based on interval pattern
_CHORD_QUALITIES = {
    "0-4-7": "maj",
    "0-3-7": "min",
    "0-4-8": "aug",
    "0-3-6": "dim",
    "0-4-7-11": "maj7",
    "0-4-7-10": "7",
    "0-3-7-10": "min7",
    "0-3-6-9": "dim7",
    "0-7": "5",
    "0-4-11": "majadd9",  # Sus4 with 9
    "0-2-7": "sus2",
    "0-5-7": "sus4",
}


def generate_chord_name(root_note: int, intervals: list) -> str:
    """
    Generate chord name from root note and intervals.

    Args:
        root_note: MIDI root note (0-127)
        intervals: List of semitone intervals from root

    Returns:
        Chord name (e.g., "Cmaj", "Amin7", "G5")
    """
    # Normalize note to name
    root_index = root_note % 12
    root_name = _NOTE_NAMES[root_index]

    # Create interval signature for chord quality
    interval_signature = "-".join(str(interval) for interval in sorted(intervals))

    chord_quality = _CHORD_QUALITIES.get(interval_signature, "??")

    return f"{root_name}{chord_quality}"
