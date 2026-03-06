"""
Harmonization Utilities - Auto-harmonize melodies, suggest chords, and analyze harmonic content.

This module provides tools for harmonizing melodies, suggesting chord progressions,
and analyzing the harmonic content of musical phrases.
"""

from typing import List, Dict, Optional
from collections import Counter

# Standard chord definitions
CHORD_INTERVALS = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dom7": [0, 4, 7, 10],
    "dim7": [0, 3, 6, 9],
    "m7b5": [0, 3, 6, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
}

# Scale definitions for harmonization
SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
}

# Diatonic chord qualities by scale degree
DIATONIC_CHORDS = {
    "major": ["maj", "min", "min", "maj", "maj", "min", "dim"],
    "minor": ["min", "dim", "maj", "min", "min", "maj", "maj"],
    "harmonic_minor": ["min", "dim", "aug", "min", "maj", "maj", "dim"],
    "melodic_minor": ["min", "min", "aug", "maj", "maj", "dim", "dim"],
}


def harmonize_melody(
    melody_notes: List[int],
    key_root: int,
    scale: str = "major",
    harmony_style: str = "triadic",
) -> List[List[int]]:
    """
    Generate chord harmonizations for a melody.

    Args:
        melody_notes: List of MIDI note numbers
        key_root: MIDI note of the key root
        scale: Scale name (major, minor, etc.)
        harmony_style: Style of harmony ("triadic", "sevenths", "fourths")

    Returns:
        List of chord note lists (one chord per melody note)

    Examples:
        >>> harmonize_melody([60, 64, 67], 60, "major", "triadic")
        [[60, 64, 67], [64, 67, 71], [67, 71, 74]]
    """
    scale_intervals = SCALE_INTERVALS.get(scale, SCALE_INTERVALS["major"])
    diatonic_qualities = DIATONIC_CHORDS.get(scale, DIATONIC_CHORDS["major"])

    harmonizations = []

    for melody_note in melody_notes:
        # Find scale degree of melody note
        interval_from_root = (melody_note - key_root) % 12

        # Find which scale degree this note is
        degree = None
        for i, interval in enumerate(scale_intervals):
            if interval == interval_from_root:
                degree = i
                break

        if degree is None:
            # Non-scale tone, use closest scale tone
            degree = _find_closest_scale_degree(interval_from_root, scale_intervals)

        # Get chord quality for this scale degree
        quality = diatonic_qualities[degree % 7]
        chord_intervals = CHORD_INTERVALS[quality]

        # Build chord under melody note (melody note as root of chord)
        if harmony_style == "triadic":
            chord = [melody_note + i for i in chord_intervals[:3]]
        elif harmony_style == "sevenths":
            chord = [melody_note + i for i in chord_intervals]
        elif harmony_style == "fourths":
            chord = _build_fourth_chord(melody_note, scale_intervals, key_root)
        else:
            chord = [melody_note + i for i in chord_intervals[:3]]

        # Ensure notes are in valid MIDI range
        chord = [n for n in chord if 0 <= n <= 127]
        harmonizations.append(chord)

    return harmonizations


def _find_closest_scale_degree(note_interval: int, scale_intervals: List[int]) -> int:
    """Find the closest scale degree for a non-scale tone."""
    min_distance = 12
    closest_degree = 0

    for i, interval in enumerate(scale_intervals):
        distance = min(
            abs(note_interval - interval), 12 - abs(note_interval - interval)
        )
        if distance < min_distance:
            min_distance = distance
            closest_degree = i

    return closest_degree


def _build_fourth_chord(
    root: int, scale_intervals: List[int], key_root: int
) -> List[int]:
    """Build a quartal (fourth-based) chord."""
    chord = [root]
    current = root

    for _ in range(3):  # Build 3 more notes
        # Find next note a perfect 4th or tritone away
        next_up = current + 5
        next_down = current - 5

        # Prefer upward motion
        if next_up <= 127:
            chord.append(next_up)
            current = next_up
        else:
            chord.append(next_down)
            current = next_down

    return chord


def suggest_chords_for_melody(
    melody_notes: List[int],
    key_root: int,
    scale: str = "major",
    max_suggestions: int = 3,
) -> List[Dict]:
    """
    Suggest possible chords for a melody sequence.

    Args:
        melody_notes: List of MIDI note numbers
        key_root: MIDI note of the key root
        scale: Scale name
        max_suggestions: Maximum suggestions per melody note

    Returns:
        List of chord suggestions with compatibility scores

    Examples:
        >>> suggest_chords_for_melody([60, 64, 67], 60, "major")
        [{"note": 60, "chords": [{"name": "C", "notes": [60,64,67], "score": 1.0}], ...}]
    """
    scale_intervals = SCALE_INTERVALS.get(scale, SCALE_INTERVALS["major"])
    scale_notes = set(key_root + i for i in scale_intervals)

    suggestions = []

    for melody_note in melody_notes:
        note_suggestions = []

        # Check all possible chord roots
        for root in range(key_root, key_root + 12):
            for chord_name, intervals in CHORD_INTERVALS.items():
                chord_notes = [root + i for i in intervals]

                # Check if melody note is in chord
                if (melody_note % 12) in [(n % 12) for n in chord_notes]:
                    # Score based on scale membership
                    scale_membership = sum(
                        1
                        for n in chord_notes
                        if (n % 12) in [(s % 12) for s in scale_notes]
                    )
                    score = scale_membership / len(chord_notes)

                    note_suggestions.append(
                        {
                            "name": f"{_note_name(root)}{chord_name}",
                            "root": root,
                            "notes": [n for n in chord_notes if 0 <= n <= 127],
                            "score": score,
                        }
                    )

        # Sort by score and take top suggestions
        note_suggestions.sort(key=lambda x: x["score"], reverse=True)
        suggestions.append(
            {
                "note": melody_note,
                "chords": note_suggestions[:max_suggestions],
            }
        )

    return suggestions


def _note_name(midi_note: int) -> str:
    """Convert MIDI note number to note name."""
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return note_names[midi_note % 12]


def analyze_harmonic_rhythm(chord_changes: List[float], tempo: float = 120.0) -> Dict:
    """
    Analyze the harmonic rhythm of a chord progression.

    Args:
        chord_changes: List of beat positions where chords change
        tempo: Tempo in BPM

    Returns:
        Analysis dictionary with rate, pattern, and complexity

    Examples:
        >>> analyze_harmonic_rhythm([0, 4, 8, 12], 120)
        {"rate": "1 chord per bar", "pattern": "regular", "complexity": "low"}
    """
    if len(chord_changes) < 2:
        return {"rate": "static", "pattern": "static", "complexity": "none"}

    # Calculate intervals between chord changes
    intervals = [
        chord_changes[i + 1] - chord_changes[i] for i in range(len(chord_changes) - 1)
    ]

    # Determine average rate
    avg_interval = sum(intervals) / len(intervals)

    if avg_interval >= 4:
        rate = "1 chord per bar (or slower)"
    elif avg_interval >= 2:
        rate = "2 chords per bar"
    elif avg_interval >= 1:
        rate = "1 chord per beat"
    else:
        rate = "multiple chords per beat"

    # Determine pattern regularity
    interval_variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)

    if interval_variance < 0.1:
        pattern = "regular"
    elif interval_variance < 1.0:
        pattern = "somewhat regular"
    else:
        pattern = "irregular"

    # Determine complexity
    unique_intervals = len(set(round(i, 1) for i in intervals))

    if unique_intervals == 1 and avg_interval >= 2:
        complexity = "low"
    elif unique_intervals <= 2 and avg_interval >= 1:
        complexity = "medium"
    else:
        complexity = "high"

    return {
        "rate": rate,
        "pattern": pattern,
        "complexity": complexity,
        "average_interval_beats": round(avg_interval, 2),
        "unique_change_patterns": unique_intervals,
    }


def generate_bass_line(
    chord_progression: List[Dict],
    style: str = "root",
    rhythm_pattern: Optional[List[float]] = None,
) -> List[Dict]:
    """
    Generate a bass line for a chord progression.

    Args:
        chord_progression: List of chord dictionaries with "root" and "notes"
        style: Bass style ("root", "walking", "arpeggio", "fifth")
        rhythm_pattern: Optional list of beat positions for notes

    Returns:
        List of bass note dictionaries

    Examples:
        >>> generate_bass_line([{"root": 60, "notes": [60,64,67]}], style="root")
        [{"pitch": 48, "start_time": 0, "duration": 4, "velocity": 100}]
    """
    bass_notes = []

    for i, chord in enumerate(chord_progression):
        root = chord["root"]
        bass_root = root - 12  # One octave below

        if style == "root":
            bass_notes.append(
                {
                    "pitch": bass_root,
                    "start_time": i * 4,
                    "duration": 4,
                    "velocity": 100,
                }
            )
        elif style == "root_fifth":
            bass_notes.extend(
                [
                    {
                        "pitch": bass_root,
                        "start_time": i * 4,
                        "duration": 2,
                        "velocity": 100,
                    },
                    {
                        "pitch": bass_root + 7,
                        "start_time": i * 4 + 2,
                        "duration": 2,
                        "velocity": 90,
                    },
                ]
            )
        elif style == "walking":
            # Simple walking pattern
            chord_tones = [n - 12 for n in chord["notes"] if n - 12 >= 36]
            for j, beat in enumerate([0, 1, 2, 3]):
                note = chord_tones[j % len(chord_tones)]
                bass_notes.append(
                    {
                        "pitch": note,
                        "start_time": i * 4 + beat,
                        "duration": 1,
                        "velocity": 100 if j == 0 else 85,
                    }
                )
        elif style == "arpeggio":
            # Simple arpeggio
            chord_tones = [n - 12 for n in chord["notes"] if n - 12 >= 36]
            for j, beat in enumerate([0, 1, 2, 2.5]):
                if j < len(chord_tones):
                    bass_notes.append(
                        {
                            "pitch": chord_tones[j],
                            "start_time": i * 4 + beat,
                            "duration": 1 if beat != 2.5 else 0.5,
                            "velocity": 100,
                        }
                    )

    # Ensure all notes are in valid MIDI range
    bass_notes = [n for n in bass_notes if 0 <= n["pitch"] <= 127]

    return bass_notes


def detect_key_from_chords(chord_roots: List[int], chord_qualities: List[str]) -> Dict:
    """
    Detect the most likely key from a chord progression.

    Args:
        chord_roots: List of MIDI root notes
        chord_qualities: List of chord quality strings

    Returns:
        Dictionary with detected key and confidence

    Examples:
        >>> detect_key_from_chords([60, 67, 69], ["maj", "maj", "min"])
        {"key": "C major", "camelot": "8B", "confidence": 0.85}
    """
    # Count chord occurrences
    root_counts = Counter([r % 12 for r in chord_roots])

    # Find chords that suggest major vs minor
    major_indicators = []
    minor_indicators = []

    for root, quality in zip(chord_roots, chord_qualities):
        root_pc = root % 12

        if quality in ["maj", "maj7", "dom7"]:
            major_indicators.append(root_pc)
        elif quality in ["min", "min7", "m7b5"]:
            minor_indicators.append(root_pc)

    # Most common major indicator is likely the key
    if major_indicators:
        major_counts = Counter(major_indicators)
        likely_major_root = major_counts.most_common(1)[0][0]
    else:
        likely_major_root = root_counts.most_common(1)[0][0]

    # Most common minor indicator could be relative minor
    if minor_indicators:
        minor_counts = Counter(minor_indicators)
        likely_minor_root = minor_counts.most_common(1)[0][0]
    else:
        # Relative minor is 9 semitones above major
        likely_minor_root = (likely_major_root + 9) % 12

    # Determine if major or minor
    major_count = sum(1 for q in chord_qualities if q in ["maj", "maj7"])
    minor_count = sum(1 for q in chord_qualities if q in ["min", "min7"])

    if major_count >= minor_count:
        detected_root = likely_major_root
        mode = "major"
        camelot_base = _get_camelot_number(detected_root, "major")
        camelot = f"{camelot_base}B"
    else:
        detected_root = likely_minor_root
        mode = "minor"
        camelot_base = _get_camelot_number(detected_root, "minor")
        camelot = f"{camelot_base}A"

    # Calculate confidence based on how well chords fit the key
    scale_intervals = SCALE_INTERVALS[mode]
    key_notes = set((detected_root + i) % 12 for i in scale_intervals)

    fitting_chords = 0
    for root in chord_roots:
        if (root % 12) in key_notes:
            fitting_chords += 1

    confidence = fitting_chords / len(chord_roots) if chord_roots else 0

    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    key_name = f"{note_names[detected_root]} {mode}"

    return {
        "key": key_name,
        "root": detected_root,
        "mode": mode,
        "camelot": camelot,
        "confidence": round(confidence, 2),
    }


def _get_camelot_number(root_pc: int, mode: str) -> int:
    """Get Camelot wheel number for a root pitch class."""
    # Camelot mapping for major keys
    major_camelot = {
        0: 8,  # C -> 8B
        1: 3,  # C# -> 3B
        2: 10,  # D -> 10B
        3: 5,  # D# -> 5B
        4: 12,  # E -> 12B
        5: 7,  # F -> 7B
        6: 2,  # F# -> 2B
        7: 9,  # G -> 9B
        8: 4,  # G# -> 4B
        9: 11,  # A -> 11B
        10: 6,  # A# -> 6B
        11: 1,  # B -> 1B
    }

    # Minor is same number, just A instead of B
    return major_camelot[root_pc]


def suggest_next_chord(
    current_chord: Dict, key_root: int, scale: str = "major", style: str = "pop"
) -> List[Dict]:
    """
    Suggest possible next chords based on music theory rules.

    Args:
        current_chord: Current chord with "root" and "quality"
        key_root: MIDI note of the key
        scale: Scale name
        style: Musical style ("pop", "jazz", "classical")

    Returns:
        List of suggested next chords with probabilities
    """
    # Common progressions by style
    progressions = {
        "pop": {
            "I": ["V", "vi", "IV"],
            "V": ["I", "vi"],
            "vi": ["IV", "V"],
            "IV": ["I", "V", "vi"],
        },
        "jazz": {
            "ii": ["V"],
            "V": ["I"],
            "I": ["ii", "vi", "iii"],
            "vi": ["ii"],
            "iii": ["vi"],
        },
        "classical": {
            "I": ["V", "IV", "vi"],
            "V": ["I", "vi"],
            "IV": ["V", "I"],
            "vi": ["ii", "IV"],
            "ii": ["V"],
        },
    }

    # Get current Roman numeral
    current_degree = _get_scale_degree(current_chord["root"], key_root, scale)
    diatonic_qualities = DIATONIC_CHORDS.get(scale, DIATONIC_CHORDS["major"])
    # current_quality = diatonic_qualities[current_degree]  # noqa: commented out - kept for reference

    roman_numerals = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
    current_roman = roman_numerals[current_degree]

    # Get possible next chords
    style_progressions = progressions.get(style, progressions["pop"])
    next_romans = style_progressions.get(current_roman, ["I", "IV", "V"])

    suggestions = []
    for roman in next_romans:
        # Convert Roman numeral back to scale degree
        next_degree = roman_numerals.index(roman.rstrip("°"))
        next_quality = diatonic_qualities[next_degree]
        next_root = key_root + SCALE_INTERVALS[scale][next_degree]

        suggestions.append(
            {
                "roman": roman,
                "root": next_root,
                "quality": next_quality,
                "name": f"{_note_name(next_root)}{next_quality}",
                "probability": 1.0 / len(next_romans),
            }
        )

    return suggestions


def _get_scale_degree(chord_root: int, key_root: int, scale: str) -> int:
    """Get the scale degree of a chord root."""
    interval = (chord_root - key_root) % 12
    scale_intervals = SCALE_INTERVALS.get(scale, SCALE_INTERVALS["major"])

    for degree, scale_interval in enumerate(scale_intervals):
        if scale_interval == interval:
            return degree

    return 0  # Default to tonic if not found


if __name__ == "__main__":
    # Test examples
    print("Harmonization Examples:")

    melody = [60, 64, 67, 72]  # C-E-G-C
    print(f"Melody: {melody}")

    harmonized = harmonize_melody(melody, 60, "major", "triadic")
    print(f"Harmonized: {harmonized}")

    suggestions = suggest_chords_for_melody(melody[:2], 60, "major")
    print(f"\nChord suggestions: {suggestions}")

    print("\nKey detection:")
    chords = detect_key_from_chords([60, 67, 69], ["maj", "maj", "min"])
    print(f"Detected key: {chords}")

    print("\nNext chord suggestions:")
    next_chords = suggest_next_chord({"root": 60, "quality": "maj"}, 60, "major", "pop")
    print(f"After C major: {next_chords}")
