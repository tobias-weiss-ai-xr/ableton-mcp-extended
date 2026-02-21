"""Voicing engine for chords (inversions, spreads, 7-3-5, etc)."""

from music_theory.chord import generate_chord_name

# Voicing templates: pattern of interval shifts relative to root.
# Format: {voicing_name: [interval_shifts]}
VOICING_TEMPLATES = {
    # Major chords
    "major": {
        "root": [0, 4, 7],  # Root position: C E G
        "drop_2": [7, 0, 4],  # Drop 2: G C E (from Cmaj triad)
        "7_3_5": [7, 3, 5],  # 7th > major 3rd > 5th
    },
    # Minor chords
    "minor": {
        "root": [0, 3, 7],
        "drop_2": [7, 0, 3],
        "7_3_5": [7, 3, 5],  # Minor 7th > minor 3rd > 5th
    },
    # 7th chords
    "maj7": {
        "root": [0, 4, 7, 11],  # Root position: C E G B
        "drop_2": [11, 0, 4, 7],  # Drop 2: B C E G (7th dropped)
        "7_3_5": [11, 4, 7],  # 7th > 3rd > 5th: B E G
        "3_7_9": [4, 11, 14],  # 3rd > 7th > 9th: E B D
    },
    "min7": {
        "root": [0, 3, 7, 10],  # Root position: C Eb G Bb
        "drop_2": [10, 0, 3, 7],  # Drop 2: Bb C Eb G
        "7_3_5": [10, 3, 7],  # 7th > minor 3rd > 5th: Bb Eb G
    },
    # Power chords
    "5": {
        "root": [0, 7],
    },
}


def generate_voicing(root_note: int, chord_quality: str, voicing_type: str) -> list:
    """
    Generate voiced chord from root note and voicing template.

    Args:
        root_note: MIDI root note (0-127)
        chord_quality: "maj", "min", "maj7", "min7", "5", etc
        voicing_type: "root", "drop_2", "7_3_5", "3_7_9"

    Returns:
        List of MIDI notes in voicing
    """
    # Step 1: Get base chord intervals from quality (e.g., maj7 → [0,4,7,11])
    from music_theory.chord import _CHORD_QUALITIES

    chord_signature = None
    for intervals_str, qual in _CHORD_QUALITIES.items():
        if qual == chord_quality:
            chord_signature = [int(interval) for interval in intervals_str.split("-")]
            break

    if not chord_signature:
        raise ValueError(f"Unknown chord quality: {chord_quality}")

    # Step 2: Apply voicing template to get note ordering
    template_key = chord_quality  # Default: use quality as template key
    # Use triad template for 7th chords if specific 7th template missing
    if (
        chord_quality.endswith("7")
        and chord_quality not in VOICING_TEMPLATES
        and chord_quality.replace("7", "") in VOICING_TEMPLATES
    ):
        template_key = chord_quality.replace("7", "")

    try:
        voicing_template = VOICING_TEMPLATES[template_key][voicing_type]
    except KeyError:
        raise ValueError(f"Unknown voicing template: {template_key}/{voicing_type}")

    # Step 3: Build MIDI notes from voicing template IN TEMPLATE ORDER
    midi_notes = []
    for template_shift in voicing_template:
        # Find the closest interval that matches template shift
        best_match_interval = _best_match_interval(template_shift, chord_signature)
        note = root_note + best_match_interval
        # Protect against MIDI 127 overflow
        if note > 127:
            note -= 12  # octave down
        # Avoid clashing with bass (MIDI < 50)
        if note < 50 and root_note >= 48:
            note += 12
        midi_notes.append(note)

    # Return exact template order (no sorting, no deduplication)
    return midi_notes


def _best_match_interval(template_shift: int, chord_signature: list) -> int:
    """Find closest chord interval that matches template shift."""
    for interval in sorted(chord_signature):
        if interval >= template_shift:
            return interval
    return chord_signature[-1]  # fallback: return highest interval
