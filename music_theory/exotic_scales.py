"""
Exotic Scales - Harmonic minor, melodic minor, whole tone, diminished, and other non-diatonic scales.

This module provides scale definitions and utilities for exotic and non-diatonic scales
used in jazz, metal, classical, and experimental electronic music.
"""

from typing import List, Dict, Optional, Tuple

# Exotic scale intervals (semitones from root)
EXOTIC_SCALES = {
    # Harmonic minor and modes
    "harmonic_minor": {
        "intervals": [0, 2, 3, 5, 7, 8, 11],
        "aliases": ["harmin", "hmin"],
        "character": "Exotic, dramatic, classical",
        "chords": ["m", "m(maj7)", "m9(maj7)"],
    },
    # Melodic minor (ascending/jazz minor) and modes
    "melodic_minor": {
        "intervals": [0, 2, 3, 5, 7, 9, 11],
        "aliases": ["melmin", "jazz_minor"],
        "character": "Sophisticated, jazzy, smooth",
        "chords": ["m(maj7)", "m6", "m9"],
    },
    # Symmetric scales
    "whole_tone": {
        "intervals": [0, 2, 4, 6, 8, 10],
        "aliases": ["wholetone", "wt"],
        "character": "Dreamy, ambiguous, floating",
        "chords": ["7#5", "aug", "7b5"],
    },
    "diminished": {
        "intervals": [0, 2, 3, 5, 6, 8, 9, 11],
        "aliases": ["octatonic", "dim"],
        "character": "Tense, cinematic, sophisticated",
        "chords": ["dim7", "m7b5", "7b9"],
    },
    "half_whole_diminished": {
        "intervals": [0, 1, 3, 4, 6, 7, 9, 10],
        "aliases": ["hwdim", "dom_dim"],
        "character": "Dominant tension, jazz",
        "chords": ["7b9", "7#9", "13b9"],
    },
    # Double harmonic (Byzantine, Arabic)
    "double_harmonic": {
        "intervals": [0, 1, 4, 5, 7, 8, 11],
        "aliases": ["byzantine", "arabic", "gypsy"],
        "character": "Middle Eastern, exotic, dramatic",
        "chords": ["maj7#5", "7b9", "m(maj7)"],
    },
    # Hungarian scales
    "hungarian_minor": {
        "intervals": [0, 2, 3, 6, 7, 8, 11],
        "aliases": ["gypsy_minor", "hungmin"],
        "character": "Gypsy, exotic, dramatic",
        "chords": ["m(maj7)", "7#5b9", "dim7"],
    },
    "hungarian_major": {
        "intervals": [0, 3, 4, 6, 7, 9, 10],
        "aliases": ["hungmaj", "lydian#2"],
        "character": "Exotic, bright, unusual",
        "chords": ["maj7#5", "7#11"],
    },
    # Neapolitan scales
    "neapolitan_minor": {
        "intervals": [0, 1, 3, 5, 7, 8, 11],
        "aliases": ["neapmin"],
        "character": "Classical, dramatic, dark",
        "chords": ["m(maj7)", "7b9"],
    },
    "neapolitan_major": {
        "intervals": [0, 1, 3, 5, 7, 9, 11],
        "aliases": ["neapmaj"],
        "character": "Classical, unusual",
        "chords": ["maj7", "7b9"],
    },
    # Enigmatic (Verdi)
    "enigmatic": {
        "intervals": [0, 1, 4, 6, 8, 10, 11],
        "aliases": ["verdi"],
        "character": "Mysterious, ethereal, classical",
        "chords": ["maj7#5", "7#5#9"],
    },
    # Persian / Oriental
    "persian": {
        "intervals": [0, 1, 4, 5, 6, 8, 11],
        "aliases": ["oriental"],
        "character": "Middle Eastern, exotic",
        "chords": ["7b5", "7b9", "m(maj7)"],
    },
    # Flamenco (Phrygian dominant)
    "phrygian_dominant": {
        "intervals": [0, 1, 4, 5, 7, 8, 10],
        "aliases": ["flamenco", "spanish", "phrydom"],
        "character": "Spanish, flamenco, intense",
        "chords": ["7b9", "7", "m"],
    },
    # Blues variations
    "hexatonic_blues": {
        "intervals": [0, 3, 5, 6, 7, 10],
        "aliases": ["blues6"],
        "character": "Bluesy, soulful",
        "chords": ["7", "m7", "7#9"],
    },
    # Bebop scales
    "bebop_dominant": {
        "intervals": [0, 2, 4, 5, 7, 9, 10, 11],
        "aliases": ["bebop_dom"],
        "character": "Jazz, bebop, 8-note",
        "chords": ["7", "9", "13"],
    },
    "bebop_major": {
        "intervals": [0, 2, 4, 5, 7, 8, 9, 11],
        "aliases": ["bebop_maj"],
        "character": "Jazz, bebop, 8-note",
        "chords": ["maj7", "6", "maj9"],
    },
    "bebop_minor": {
        "intervals": [0, 2, 3, 4, 5, 7, 9, 10],
        "aliases": ["bebop_min"],
        "character": "Jazz, bebop, 8-note",
        "chords": ["m7", "m9", "m6"],
    },
    # Chromatic approaches
    "chromatic": {
        "intervals": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        "aliases": ["all_notes"],
        "character": "Atonal, free, dissonant",
        "chords": ["any"],
    },
}

# Modes of melodic minor
MELODIC_MINOR_MODES = {
    "melodic_minor": {
        "intervals": [0, 2, 3, 5, 7, 9, 11],
        "mode_of": "melodic_minor",
        "degree": 1,
        "name": "Melodic Minor",
        "character": "Sophisticated minor",
    },
    "dorian_flat2": {
        "intervals": [0, 1, 3, 5, 7, 9, 10],
        "mode_of": "melodic_minor",
        "degree": 2,
        "name": "Dorian b2 (Phrygian #6)",
        "character": "Exotic, jazz",
    },
    "lydian_augmented": {
        "intervals": [0, 2, 4, 6, 8, 9, 11],
        "mode_of": "melodic_minor",
        "degree": 3,
        "name": "Lydian Augmented",
        "character": "Dreamy, augmented",
    },
    "lydian_dominant": {
        "intervals": [0, 2, 4, 6, 7, 9, 10],
        "mode_of": "melodic_minor",
        "degree": 4,
        "name": "Lydian Dominant",
        "character": "Jazz, dominant with #11",
    },
    "mixolydian_flat6": {
        "intervals": [0, 2, 4, 5, 7, 8, 10],
        "mode_of": "melodic_minor",
        "degree": 5,
        "name": "Mixolydian b6 (Fifth Mode)",
        "character": "Jazz, dominant",
    },
    "locrian_sharp2": {
        "intervals": [0, 2, 3, 5, 6, 8, 10],
        "mode_of": "melodic_minor",
        "degree": 6,
        "name": "Locrian #2 (Half-Diminished)",
        "character": "Jazz, tension",
    },
    "super_locrian": {
        "intervals": [0, 1, 3, 4, 6, 8, 10],
        "mode_of": "melodic_minor",
        "degree": 7,
        "name": "Super Locrian (Altered Scale)",
        "character": "All alterations, jazz",
    },
}

# Modes of harmonic minor
HARMONIC_MINOR_MODES = {
    "harmonic_minor": {
        "intervals": [0, 2, 3, 5, 7, 8, 11],
        "mode_of": "harmonic_minor",
        "degree": 1,
        "name": "Harmonic Minor",
        "character": "Classical, dramatic",
    },
    "locrian_sharp6": {
        "intervals": [0, 1, 3, 5, 6, 9, 10],
        "mode_of": "harmonic_minor",
        "degree": 2,
        "name": "Locrian #6",
        "character": "Dark, tense",
    },
    "ionian_sharp5": {
        "intervals": [0, 2, 4, 5, 8, 9, 11],
        "mode_of": "harmonic_minor",
        "degree": 3,
        "name": "Ionian #5",
        "character": "Augmented, bright",
    },
    "dorian_sharp4": {
        "intervals": [0, 2, 3, 6, 7, 9, 10],
        "mode_of": "harmonic_minor",
        "degree": 4,
        "name": "Dorian #4",
        "character": "Exotic, jazz",
    },
    "phrygian_dominant": {
        "intervals": [0, 1, 4, 5, 7, 8, 10],
        "mode_of": "harmonic_minor",
        "degree": 5,
        "name": "Phrygian Dominant (Spanish)",
        "character": "Spanish, flamenco",
    },
    "lydian_sharp2": {
        "intervals": [0, 3, 4, 6, 7, 9, 11],
        "mode_of": "harmonic_minor",
        "degree": 6,
        "name": "Lydian #2",
        "character": "Exotic, bright",
    },
    "ultralocrian": {
        "intervals": [0, 1, 3, 4, 6, 8, 9],
        "mode_of": "harmonic_minor",
        "degree": 7,
        "name": "Ultralocrian",
        "character": "Very tense, dissonant",
    },
}


def get_exotic_scale(scale_name: str) -> Dict:
    """
    Get exotic scale information by name or alias.

    Args:
        scale_name: Scale name or alias (case-insensitive)

    Returns:
        Dict with intervals, aliases, character, and chords

    Examples:
        >>> get_exotic_scale("harmonic_minor")
        {"intervals": [0,2,3,5,7,8,11], "character": "Exotic, dramatic", ...}
    """
    scale_name_lower = scale_name.lower().replace(" ", "_")

    # Check main scales
    if scale_name_lower in EXOTIC_SCALES:
        return EXOTIC_SCALES[scale_name_lower]

    # Check melodic minor modes
    if scale_name_lower in MELODIC_MINOR_MODES:
        return MELODIC_MINOR_MODES[scale_name_lower]

    # Check harmonic minor modes
    if scale_name_lower in HARMONIC_MINOR_MODES:
        return HARMONIC_MINOR_MODES[scale_name_lower]

    # Check aliases
    for scale_key, scale_data in EXOTIC_SCALES.items():
        if "aliases" in scale_data:
            if scale_name_lower in [a.lower() for a in scale_data["aliases"]]:
                return scale_data

    raise ValueError(f"Unknown exotic scale: {scale_name}")


def generate_exotic_scale_notes(
    root: int, scale_name: str, octaves: int = 1
) -> List[int]:
    """
    Generate MIDI notes for an exotic scale.

    Args:
        root: MIDI root note (0-127)
        scale_name: Scale name or alias
        octaves: Number of octaves to generate (default 1)

    Returns:
        List of MIDI notes in the scale

    Examples:
        >>> generate_exotic_scale_notes(60, "harmonic_minor")
        [60, 62, 63, 65, 67, 68, 71]  # C harmonic minor

        >>> generate_exotic_scale_notes(60, "whole_tone", octaves=2)
        [60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 80, 82]
    """
    scale_data = get_exotic_scale(scale_name)
    intervals = scale_data["intervals"]

    notes = []
    for octave in range(octaves):
        for interval in intervals:
            note = root + interval + (octave * 12)
            if note <= 127:
                notes.append(note)

    return notes


def suggest_chords_for_exotic_scale(scale_name: str) -> List[str]:
    """
    Suggest chords that work with an exotic scale.

    Args:
        scale_name: Scale name or alias

    Returns:
        List of suggested chord types

    Examples:
        >>> suggest_chords_for_exotic_scale("harmonic_minor")
        ["m", "m(maj7)", "m9(maj7)"]
    """
    scale_data = get_exotic_scale(scale_name)
    return scale_data.get("chords", [])


def get_scale_character(scale_name: str) -> str:
    """
    Get the character/mood description of a scale.

    Args:
        scale_name: Scale name or alias

    Returns:
        Character description string
    """
    scale_data = get_exotic_scale(scale_name)
    return scale_data.get("character", "Unknown")


def compare_scales(scale1: str, scale2: str) -> Dict:
    """
    Compare two scales to see their relationship.

    Args:
        scale1: First scale name
        scale2: Second scale name

    Returns:
        Dict with shared_notes, unique_to_1, unique_to_2, similarity

    Examples:
        >>> compare_scales("harmonic_minor", "melodic_minor")
        {"shared_notes": 6, "similarity": 0.86, ...}
    """
    s1 = get_exotic_scale(scale1)
    s2 = get_exotic_scale(scale2)

    intervals1 = set(s1["intervals"])
    intervals2 = set(s2["intervals"])

    shared = intervals1 & intervals2
    unique1 = intervals1 - intervals2
    unique2 = intervals2 - intervals1

    total = len(intervals1 | intervals2)
    similarity = len(shared) / total if total > 0 else 0

    return {
        "scale1": scale1,
        "scale2": scale2,
        "shared_intervals": sorted(list(shared)),
        "unique_to_scale1": sorted(list(unique1)),
        "unique_to_scale2": sorted(list(unique2)),
        "shared_notes": len(shared),
        "similarity": round(similarity, 2),
    }


def get_compatible_exotic_scales(
    scale_name: str, min_similarity: float = 0.7
) -> List[Tuple[str, float]]:
    """
    Find scales that are similar/compatible with the given scale.

    Args:
        scale_name: Scale name to find compatibles for
        min_similarity: Minimum similarity threshold (0-1)

    Returns:
        List of (scale_name, similarity) tuples sorted by similarity

    Examples:
        >>> get_compatible_exotic_scales("harmonic_minor", 0.6)
        [("melodic_minor", 0.86), ("phrygian_dominant", 0.71), ...]
    """
    all_scales = (
        list(EXOTIC_SCALES.keys())
        + list(MELODIC_MINOR_MODES.keys())
        + list(HARMONIC_MINOR_MODES.keys())
    )

    compatibles = []
    for other_scale in all_scales:
        if other_scale != scale_name:
            comparison = compare_scales(scale_name, other_scale)
            if comparison["similarity"] >= min_similarity:
                compatibles.append((other_scale, comparison["similarity"]))

    return sorted(compatibles, key=lambda x: x[1], reverse=True)


def generate_exotic_melody(
    root: int,
    scale_name: str,
    length: int = 8,
    rhythm_pattern: Optional[List[float]] = None,
) -> List[Dict]:
    """
    Generate a simple melody in an exotic scale.

    Args:
        root: MIDI root note
        scale_name: Scale name
        length: Number of notes to generate
        rhythm_pattern: Optional list of start times (beats)

    Returns:
        List of note dictionaries with pitch, start_time, duration

    Examples:
        >>> generate_exotic_melody(60, "harmonic_minor", length=4)
        [{"pitch": 60, "start_time": 0, "duration": 1}, ...]
    """
    import random

    notes_in_scale = generate_exotic_scale_notes(root, scale_name, octaves=2)

    if rhythm_pattern is None:
        rhythm_pattern = [i * 0.5 for i in range(length)]

    melody = []
    for i, start_time in enumerate(rhythm_pattern[:length]):
        # Random note from scale (weighted toward root and 5th)
        weights = [3 if n == root or n == root + 7 else 1 for n in notes_in_scale]
        pitch = random.choices(notes_in_scale, weights=weights)[0]

        melody.append(
            {
                "pitch": pitch,
                "start_time": start_time,
                "duration": 0.5,  # Default duration
                "velocity": 100,
            }
        )

    return melody


def list_all_exotic_scales() -> List[str]:
    """List all available exotic scale names."""
    return list(EXOTIC_SCALES.keys())


def list_melodic_minor_modes() -> List[str]:
    """List all modes of melodic minor."""
    return list(MELODIC_MINOR_MODES.keys())


def list_harmonic_minor_modes() -> List[str]:
    """List all modes of harmonic minor."""
    return list(HARMONIC_MINOR_MODES.keys())


if __name__ == "__main__":
    # Test examples
    print("Exotic Scale Examples:")
    print(f"C harmonic minor: {generate_exotic_scale_notes(60, 'harmonic_minor')}")
    print(f"C melodic minor: {generate_exotic_scale_notes(60, 'melodic_minor')}")
    print(f"C whole tone: {generate_exotic_scale_notes(60, 'whole_tone')}")
    print(f"C diminished: {generate_exotic_scale_notes(60, 'diminished')}")
    print(
        f"C Phrygian dominant: {generate_exotic_scale_notes(60, 'phrygian_dominant')}"
    )

    print("\nScale comparison:")
    print(compare_scales("harmonic_minor", "melodic_minor"))

    print("\nCompatible scales for harmonic_minor:")
    print(get_compatible_exotic_scales("harmonic_minor", 0.6)[:5])

    print("\nAll exotic scales:")
    print(list_all_exotic_scales())
