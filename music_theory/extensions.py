"""
Extended Chord Theory - 9th, 11th, 13th chords and altered dominants.

This module provides chord construction for extended harmonies used in jazz,
neo-soul, R&B, and sophisticated electronic music.
"""

from typing import List, Optional

# Extended chord intervals (semitones from root)
EXTENDED_CHORDS = {
    # 9th chords (5 notes)
    "maj9": [0, 4, 7, 11, 14],  # Major 9: R-3-5-7-9
    "min9": [0, 3, 7, 10, 14],  # Minor 9: R-b3-5-b7-9
    "dom9": [0, 4, 7, 10, 14],  # Dominant 9: R-3-5-b7-9
    "dim9": [0, 3, 6, 9, 14],  # Diminished 9: R-b3-b5-bb7-9
    # 11th chords (6 notes)
    "maj11": [0, 4, 7, 11, 14, 17],  # Major 11: R-3-5-7-9-11 (rare, clashes)
    "min11": [0, 3, 7, 10, 14, 17],  # Minor 11: R-b3-5-b7-9-11 (very common)
    "dom11": [0, 4, 7, 10, 14, 17],  # Dominant 11: R-3-5-b7-9-11 (often omit 3)
    # 13th chords (7 notes - often voiced with fewer notes)
    "maj13": [0, 4, 7, 11, 14, 17, 21],  # Major 13: R-3-5-7-9-11-13
    "min13": [0, 3, 7, 10, 14, 17, 21],  # Minor 13: R-b3-5-b7-9-11-13
    "dom13": [0, 4, 7, 10, 14, 17, 21],  # Dominant 13: R-3-5-b7-9-11-13
    # 6th chords
    "maj6": [0, 4, 7, 9],  # Major 6: R-3-5-6
    "min6": [0, 3, 7, 9],  # Minor 6: R-b3-5-6
    "maj6/9": [0, 4, 7, 9, 14],  # Major 6/9: R-3-5-6-9
    # Add chords
    "add9": [0, 4, 7, 14],  # Add 9: R-3-5-9
    "minadd9": [0, 3, 7, 14],  # Minor add 9: R-b3-5-9
    "add11": [0, 4, 7, 17],  # Add 11: R-3-5-11
    "add2": [0, 2, 4, 7],  # Add 2: R-2-3-5
}

# Altered dominant intervals
ALTERED_CHORDS = {
    # Flat alterations
    "7b5": [0, 4, 6, 10],  # Dominant 7 flat 5
    "7b9": [0, 4, 7, 10, 13],  # Dominant 7 flat 9
    "7b13": [0, 4, 7, 10, 20],  # Dominant 7 flat 13
    # Sharp alterations
    "7#5": [0, 4, 8, 10],  # Dominant 7 sharp 5 (augmented 7)
    "7#9": [0, 4, 7, 10, 15],  # Dominant 7 sharp 9 (Hendrix chord)
    "7#11": [0, 4, 7, 10, 18],  # Dominant 7 sharp 11 (Lydian dominant)
    # Combined alterations
    "7b5b9": [0, 4, 6, 10, 13],  # Dominant 7 flat 5 flat 9
    "7b5#9": [0, 4, 6, 10, 15],  # Dominant 7 flat 5 sharp 9
    "7#5b9": [0, 4, 8, 10, 13],  # Dominant 7 sharp 5 flat 9
    "7#5#9": [0, 4, 8, 10, 15],  # Dominant 7 sharp 5 sharp 9
    # Full altered (all alterations)
    "7alt": [0, 4, 8, 10, 13, 15],  # Dominant 7 altered (b5, #5, b9, #9)
    # Diminished dominants
    "7b9b13": [0, 4, 7, 10, 13, 20],  # Dominant 7 flat 9 flat 13
    "dim7": [0, 3, 6, 9],  # Diminished 7
    "m7b5": [0, 3, 6, 10],  # Half-diminished (minor 7 flat 5)
}

# Common voicings for extended chords
VOICING_TEMPLATES = {
    # Rootless voicings (no bass note - for ensemble playing)
    "rootless_9": {
        "maj9": [7, 11, 14],  # 5-7-9
        "min9": [7, 10, 14],  # 5-b7-9
        "dom9": [7, 10, 14],  # 5-b7-9
    },
    "rootless_11": {
        "min11": [7, 10, 14, 17],  # 5-b7-9-11
        "dom11": [7, 10, 14, 17],  # 5-b7-9-11
    },
    "rootless_13": {
        "maj13": [7, 11, 14, 21],  # 5-7-9-13
        "min13": [7, 10, 14, 21],  # 5-b7-9-13
        "dom13": [7, 10, 14, 21],  # 5-b7-9-13
    },
    # Shell voicings (essential notes only)
    "shell": {
        "maj9": [4, 11],  # 3-7
        "min9": [3, 10],  # b3-b7
        "dom9": [4, 10],  # 3-b7
        "dom13": [4, 10, 21],  # 3-b7-13
    },
    # So What voicings (4th chords)
    "fourths": {
        "min11": [7, 10, 14, 17],  # 5-b7-9-11 (stacked 4ths)
        "min9": [3, 7, 10, 14],  # b3-5-b7-9
    },
    # Kenny Barron voicings (5-note, spread)
    "barron": {
        "min11": [3, 7, 10, 14, 17],  # b3-5-b7-9-11
        "maj9": [4, 7, 11, 14, 17],  # 3-5-7-9-11(#)
    },
}


def create_extended_chord(
    root: int, chord_type: str, voicing: Optional[str] = None
) -> List[int]:
    """
    Create an extended chord (9th, 11th, 13th).

    Args:
        root: MIDI root note (0-127)
        chord_type: Chord type (e.g., "maj9", "min11", "dom13")
        voicing: Optional voicing type ("rootless_9", "shell", "fourths", etc.)

    Returns:
        List of MIDI notes in the chord

    Examples:
        >>> create_extended_chord(60, "min9")
        [60, 63, 67, 70, 74]  # C-Eb-G-Bb-D

        >>> create_extended_chord(60, "min11", voicing="rootless_11")
        [67, 70, 74, 77]  # G-Bb-D-F (rootless Cm11)
    """
    # Check if voicing requested
    if voicing and voicing in VOICING_TEMPLATES:
        if chord_type in VOICING_TEMPLATES[voicing]:
            intervals = VOICING_TEMPLATES[voicing][chord_type]
        else:
            # Fall back to full chord
            intervals = EXTENDED_CHORDS.get(chord_type)
    else:
        intervals = EXTENDED_CHORDS.get(chord_type)

    if intervals is None:
        raise ValueError(f"Unknown chord type: {chord_type}")

    # Build MIDI notes
    notes = []
    for interval in intervals:
        note = root + interval
        # Protect against MIDI overflow
        if note <= 127:
            notes.append(note)

    return notes


def create_altered_chord(
    root: int, alterations: List[str], base: str = "7"
) -> List[int]:
    """
    Create an altered dominant chord.

    Args:
        root: MIDI root note (0-127)
        alterations: List of alterations (e.g., ["b5", "#9"])
        base: Base chord type (default "7" for dominant 7)

    Returns:
        List of MIDI notes in the altered chord

    Examples:
        >>> create_altered_chord(60, ["#9"])  # C7#9 (Hendrix chord)
        [60, 64, 67, 70, 75]  # C-E-G-Bb-D#

        >>> create_altered_chord(60, ["b5", "b9"])  # C7b5b9
        [60, 64, 66, 70, 73]  # C-E-Gb-Bb-Db
    """
    # Sort alterations to match predefined chords
    alterations_sorted = sorted(alterations)
    alt_key = base + "".join(alterations_sorted)

    # Try to find predefined chord
    if alt_key in ALTERED_CHORDS:
        intervals = ALTERED_CHORDS[alt_key]
    else:
        # Build chord manually
        intervals = _build_altered_intervals(base, alterations)

    # Build MIDI notes
    notes = []
    for interval in intervals:
        note = root + interval
        if note <= 127:
            notes.append(note)

    return notes


def _build_altered_intervals(base: str, alterations: List[str]) -> List[int]:
    """Build intervals for altered chord from base and alterations."""
    # Start with dominant 7
    intervals = [0, 4, 7, 10]  # R-3-5-b7

    alteration_map = {
        "b5": (2, 6),  # Replace 5 with b5
        "#5": (2, 8),  # Replace 5 with #5
        "b9": (None, 13),  # Add b9
        "#9": (None, 15),  # Add #9
        "#11": (None, 18),  # Add #11
        "b13": (None, 20),  # Add b13
    }

    for alt in alterations:
        if alt in alteration_map:
            replace_idx, value = alteration_map[alt]
            if replace_idx is not None:
                intervals[replace_idx] = value
            else:
                intervals.append(value)

    return sorted(intervals)


def suggest_extension(chord_type: str, context: str = "jazz") -> List[str]:
    """
    Suggest appropriate extensions for a chord based on context.

    Args:
        chord_type: Base chord type (e.g., "maj7", "min7", "7")
        context: Musical context ("jazz", "neo_soul", "rnb", "house")

    Returns:
        List of suggested extended chord types

    Examples:
        >>> suggest_extension("min7", "jazz")
        ["min9", "min11"]

        >>> suggest_extension("maj7", "neo_soul")
        ["maj9", "maj7#11"]
    """
    suggestions = {
        "jazz": {
            "maj7": ["maj9", "maj7#11"],
            "min7": ["min9", "min11"],
            "7": ["9", "13", "7b9", "7#9"],
            "m7b5": ["m7b5", "m9b5"],
        },
        "neo_soul": {
            "maj7": ["maj9", "maj7#11", "maj13"],
            "min7": ["min9", "min11", "min13"],
            "7": ["9", "11", "13"],
            "dom7": ["9", "13"],
        },
        "rnb": {
            "maj7": ["maj9", "add9"],
            "min7": ["min9", "min11"],
            "7": ["9", "13"],
        },
        "house": {
            "maj7": ["maj9", "add9"],
            "min7": ["min9", "min11"],
            "7": ["9", "7sus4"],
        },
    }

    return suggestions.get(context, {}).get(chord_type, [])


def create_voiced_extension(
    root: int,
    chord_type: str,
    voicing_type: str = "drop_2",
    top_note: Optional[int] = None,
) -> List[int]:
    """
    Create an extended chord with specific voicing.

    Args:
        root: MIDI root note
        chord_type: Extended chord type (e.g., "min11")
        voicing_type: Voicing style ("drop_2", "drop_3", "open", "close")
        top_note: Optional target top note for voice leading

    Returns:
        List of MIDI notes in the voiced chord
    """
    # Get base chord
    notes = create_extended_chord(root, chord_type)

    if voicing_type == "drop_2":
        # Drop 2nd note from top down an octave
        if len(notes) >= 2:
            notes[-2] -= 12
    elif voicing_type == "drop_3":
        # Drop 3rd note from top down an octave
        if len(notes) >= 3:
            notes[-3] -= 12
    elif voicing_type == "open":
        # Spread notes across octaves
        notes = _spread_voicing(notes)

    # Adjust top note if specified
    if top_note is not None:
        notes = _adjust_top_note(notes, top_note)

    # Sort and remove duplicates
    notes = sorted(set(notes))

    # Ensure all notes are in valid MIDI range
    notes = [n for n in notes if 0 <= n <= 127]

    return notes


def _spread_voicing(notes: List[int]) -> List[int]:
    """Spread voicing across octaves for fuller sound."""
    if len(notes) <= 3:
        return notes

    result = []
    for i, note in enumerate(notes):
        if i % 2 == 1 and note + 12 <= 127:
            result.append(note + 12)
        else:
            result.append(note)

    return result


def _adjust_top_note(notes: List[int], target: int) -> List[int]:
    """Adjust chord voicing to have specific top note."""
    if not notes:
        return notes

    current_top = max(notes)
    diff = target - current_top

    # Transpose entire chord
    return [n + diff for n in notes]


# Predefined chord dictionaries for quick lookup
NINTH_CHORDS = {
    k: v
    for k, v in EXTENDED_CHORDS.items()
    if "9" in k and "11" not in k and "13" not in k
}
ELEVENTH_CHORDS = {
    k: v for k, v in EXTENDED_CHORDS.items() if "11" in k and "13" not in k
}
THIRTEENTH_CHORDS = {k: v for k, v in EXTENDED_CHORDS.items() if "13" in k}


if __name__ == "__main__":
    # Test examples
    print("Extended Chord Examples:")
    print(f"Cmin9: {create_extended_chord(60, 'min9')}")
    print(f"Cmin11: {create_extended_chord(60, 'min11')}")
    print(
        f"Cmin11 (rootless): {create_extended_chord(60, 'min11', voicing='rootless_11')}"
    )
    print(f"C7#9 (Hendrix): {create_altered_chord(60, ['#9'])}")
    print(f"C7b5b9: {create_altered_chord(60, ['b5', 'b9'])}")
    print(f"Suggested extensions for min7 in jazz: {suggest_extension('min7', 'jazz')}")
