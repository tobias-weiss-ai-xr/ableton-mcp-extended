"""Arpeggiator for chords (strum patterns, swing, direction)."""

from typing import List, Dict, Optional, Union


def arpeggiate_chord(
    midi_notes: List[int],
    rate: str = "1/8",
    direction: str = "up",
    swing: float = 0.0,
    repeats: int = 1,
) -> List[Dict[str, Union[int, float]]]:
    """
    Arpeggiate a chord into rhythmic strum patterns.

    Args:
        midi_notes: List of MIDI note numbers (voicing order preserved)
        rate: Note density: "1/4", "1/8", "1/16", "1/32", "triplet"
        direction: Pattern direction: "up", "down", "random"
        swing: Swing percentage (0-1.0, 0.5 = 50%)
        repeats: Number of repeats (1 = play once)

    Returns:
        List of notes with timing envelope:
        [
            {"pitch": 60, "start_time": 0.0, "duration": 0.5},
            ...
        ]
    """
    if not midi_notes:
        return []

    # Normalize rate to beats per note
    rate_to_beats = {
        "1/4": 1.0,
        "1/8": 0.5,
        "1/16": 0.25,
        "1/32": 0.125,
        "triplet": 0.333,  # 1/8 triplet
    }

    try:
        interval = rate_to_beats[rate.lower()]
    except KeyError:
        raise ValueError(f"Unsupported rate: {rate}")

    total_duration = interval * len(midi_notes) * repeats
    arpeggiated_notes = []

    for repeat in range(repeats):
        notes_to_play = list(midi_notes)  # Preserve voicing order
        if direction == "down":
            notes_to_play = sorted(notes_to_play, reverse=True)
        elif direction == "random":
            import random

            random.shuffle(notes_to_play)

        for i, note in enumerate(notes_to_play):
            # Apply swing: delay odd-numbered notes for 8th/16th
            time_offset = i * interval
            if i % 2 == 1 and swing > 0:
                time_offset += (
                    swing * interval * 0.5
                )  # Swing: delay off-beats by swing% of half interval → 0.2 * 0.125 = 0.025

            start_time = (repeat * len(midi_notes) * interval) + time_offset

            # Protect against MIDI range overflow
            safe_note = min(note, 127)

            arpeggiated_notes.append(
                {
                    "pitch": safe_note,
                    "start_time": round(start_time, 3),
                    "duration": interval * 0.8,  # 80% of interval for note length
                }
            )

    return arpeggiated_notes
