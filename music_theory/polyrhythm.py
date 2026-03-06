"""
Polyrhythm and Tuplet Generators - Create complex rhythmic patterns.

This module provides utilities for generating polyrhythms, tuplets,
and other complex rhythmic patterns for electronic music.
"""

from typing import List, Dict, Optional, Tuple
import math



def create_polyrhythm(
    ratio: Tuple[int, int],
    base_duration: float = 4.0,
    midi_notes: Optional[List[int]] = None,
    velocity: int = 100,
    start_times: Optional[List[float]] = None,
) -> List[Dict]:
    """
    Create a polyrhythm with two layers.

    Args:
        ratio: Tuple of (numerator, denominator) for the polyrhythm
        base_duration: Total duration in beats
        midi_notes: Optional list of 2 MIDI notes (one per layer)
        velocity: Note velocity (0-127)
        start_times: Optional list of start times for each layer

    Returns:
        List of note dictionaries

    Examples:
        >>> create_polyrhythm((3, 2), 4, [60, 62])  # 3:2 polyrhythm
        [{"pitch": 60, "start_time": 0, ...}, ...]
    """
    if midi_notes is None:
        midi_notes = [60, 62]  # Default to C and D

    if len(midi_notes) < 2:
        midi_notes = midi_notes + [midi_notes[0] + 2]

    layer1_count, layer2_count = ratio

    # Calculate timing for each layer
    layer1_interval = base_duration / layer1_count
    layer2_interval = base_duration / layer2_count

    notes = []

    # Layer 1 notes
    for i in range(layer1_count):
        notes.append(
            {
                "pitch": midi_notes[0],
                "start_time": i * layer1_interval,
                "duration": layer1_interval * 0.8,
                "velocity": velocity,
            }
        )

    # Layer 2 notes
    for i in range(layer2_count):
        notes.append(
            {
                "pitch": midi_notes[1],
                "start_time": i * layer2_interval,
                "duration": layer2_interval * 0.8,
                "velocity": velocity,
            }
        )

    # Sort by start time
    notes.sort(key=lambda x: x["start_time"])

    return notes


def create_triplet(
    note_value: str = "8th", count: int = 3, root_note: int = 60, velocity: int = 100
) -> List[Dict]:
    """
    Create a triplet figure.

    Args:
        note_value: Base note value ("4th", "8th", "16th", "quarter", "half")
        count: Number of notes in the tuplet (3 for triplet)
        root_note: Starting MIDI note
        velocity: Note velocity

    Returns:
        List of triplet notes

    Examples:
        >>> create_triplet("8th", 3, 60)  # 8th note triplet
        [{"pitch": 60, "start_time": 0, "duration": 0.33, ...}, ...]
    """
    # Base durations in beats
    note_durations = {
        "whole": 4.0,
        "half": 2.0,
        "quarter": 1.0,
        "4th": 1.0,
        "8th": 0.5,
        "16th": 0.25,
        "32nd": 0.125,
    }

    base_duration = note_durations.get(note_value, 0.5)
    # Triplet: 3 notes in the space of 2
    tuplet_duration = base_duration * 2 / count
    note_duration = tuplet_duration * 0.9  # Slightly shorter for articulation

    notes = []
    for i in range(count):
        notes.append(
            {
                "pitch": root_note,
                "start_time": i * tuplet_duration,
                "duration": note_duration,
                "velocity": velocity,
            }
        )

    return notes


def create_quintuplet(
    note_value: str = "8th", root_note: int = 60, velocity: int = 100
) -> List[Dict]:
    """
    Create a quintuplet (5 notes in the space of 4).

    Args:
        note_value: Base note value
        root_note: MIDI note
        velocity: Note velocity

    Returns:
        List of quintuplet notes
    """
    return create_tuplet(note_value, 5, root_note, velocity)


def create_sextuplet(
    note_value: str = "16th", root_note: int = 60, velocity: int = 100
) -> List[Dict]:
    """
    Create a sextuplet (6 notes in the space of 4).

    Args:
        note_value: Base note value
        root_note: MIDI note
        velocity: Note velocity

    Returns:
        List of sextuplet notes
    """
    return create_tuplet(note_value, 6, root_note, velocity)


def create_tuplet(
    note_value: str,
    numerator: int,
    root_note: int = 60,
    velocity: int = 100,
    denominator: Optional[int] = None,
) -> List[Dict]:
    """
    Create a general tuplet (numerator notes in denominator space).

    Args:
        note_value: Base note value
        numerator: Number of notes to play
        root_note: MIDI note
        velocity: Note velocity
        denominator: Space to fit in (default: numerator - 1)

    Returns:
        List of tuplet notes

    Examples:
        >>> create_tuplet("8th", 5, 60)  # 5:4 quintuplet
        >>> create_tuplet("8th", 7, 60, 100, 4)  # 7:4 septuplet
    """
    if denominator is None:
        denominator = numerator - 1 if numerator > 2 else 2

    note_durations = {
        "whole": 4.0,
        "half": 2.0,
        "quarter": 1.0,
        "4th": 1.0,
        "8th": 0.5,
        "16th": 0.25,
        "32nd": 0.125,
    }

    base_duration = note_durations.get(note_value, 0.5)
    total_duration = base_duration * denominator
    note_interval = total_duration / numerator
    note_duration = note_interval * 0.9

    notes = []
    for i in range(numerator):
        notes.append(
            {
                "pitch": root_note,
                "start_time": i * note_interval,
                "duration": note_duration,
                "velocity": velocity,
            }
        )

    return notes


def create_hemiola(
    root_note: int = 60, bars: int = 2, velocity: int = 100
) -> List[Dict]:
    """
    Create a hemiola (3:2 polyrhythm over 2 bars).

    The hemiola is a classic rhythmic device where 3 notes are played
    in the space normally taken by 2, creating a temporary 3/4 feel
    within 2/4 or 4/4 time.

    Args:
        root_note: MIDI note
        bars: Number of bars (default 2)
        velocity: Note velocity

    Returns:
        List of hemiola notes

    Examples:
        >>> create_hemiola(60)  # Classic 3:2 hemiola
        [{"pitch": 60, "start_time": 0, ...}, {"pitch": 60, "start_time": 1.33, ...}, ...]
    """
    total_duration = bars * 4  # Assuming 4/4 time

    # 3 notes evenly spaced over 2 bars (8 beats)
    interval = total_duration / 3

    notes = []
    for i in range(3):
        notes.append(
            {
                "pitch": root_note,
                "start_time": i * interval,
                "duration": interval * 0.8,
                "velocity": velocity,
            }
        )

    return notes


def create_cross_rhythm(
    pattern1: List[int],
    pattern2: List[int],
    base_duration: float = 4.0,
    midi_notes: Optional[List[int]] = None,
    velocity: int = 100,
) -> List[Dict]:
    """
    Create a cross-rhythm from two rhythmic patterns.

    Args:
        pattern1: First pattern (list of beat subdivisions)
        pattern2: Second pattern (list of beat subdivisions)
        base_duration: Total duration in beats
        midi_notes: MIDI notes for each pattern
        velocity: Note velocity

    Returns:
        List of cross-rhythm notes

    Examples:
        >>> create_cross_rhythm([1,0,1,0], [1,0,0], 4, [60, 62])
        # Pattern 1: X-X- (every 2 beats)
        # Pattern 2: X-- (every 3 beats)
    """
    if midi_notes is None:
        midi_notes = [60, 62]

    notes = []

    # Calculate cycle lengths
    cycle1 = len(pattern1)
    cycle2 = len(pattern2)

    # Find LCM for full cycle
    # LCM for full cycle (not directly used, kept for reference)

    # Generate pattern 1
    beat_interval1 = base_duration / cycle1
    time = 0
    for i, hit in enumerate(pattern1):
        if hit:
            notes.append(
                {
                    "pitch": midi_notes[0],
                    "start_time": time,
                    "duration": beat_interval1 * 0.8,
                    "velocity": velocity,
                }
            )
        time += beat_interval1

    # Generate pattern 2
    beat_interval2 = base_duration / cycle2
    time = 0
    for i, hit in enumerate(pattern2):
        if hit:
            notes.append(
                {
                    "pitch": midi_notes[1],
                    "start_time": time,
                    "duration": beat_interval2 * 0.8,
                    "velocity": velocity,
                }
            )
        time += beat_interval2

    notes.sort(key=lambda x: x["start_time"])
    return notes


def create_additive_rhythm(
    pattern: List[int], root_note: int = 60, velocity: int = 100
) -> List[Dict]:
    """
    Create an additive rhythm from a pattern of beat groupings.

    Additive rhythms are built by combining irregular groups of beats,
    common in Balkan, Indian, and African music.

    Args:
        pattern: List of beat groupings (e.g., [3, 3, 2] for 3+3+2)
        root_note: MIDI note
        velocity: Note velocity

    Returns:
        List of additive rhythm notes

    Examples:
        >>> create_additive_rhythm([3, 3, 2], 60)  # 3+3+2 = 8 beats
        # Groups of 3, 3, 2 beats with accents on group starts
    """
    notes = []
    time = 0

    for group_size in pattern:
        # Accent first note of each group
        notes.append(
            {
                "pitch": root_note,
                "start_time": time,
                "duration": 0.8,
                "velocity": velocity,  # Accent
            }
        )

        # Add non-accented notes for rest of group
        for i in range(1, group_size):
            notes.append(
                {
                    "pitch": root_note,
                    "start_time": time + i,
                    "duration": 0.8,
                    "velocity": int(velocity * 0.7),  # Non-accent
                }
            )

        time += group_size

    return notes


def create_odd_time_pattern(
    time_signature: Tuple[int, int],
    pattern_style: str = "straight",
    root_note: int = 60,
    velocity: int = 100,
) -> List[Dict]:
    """
    Create a pattern in an odd time signature.

    Args:
        time_signature: Tuple of (numerator, denominator)
        pattern_style: Style of pattern ("straight", "syncopated", "asymmetric")
        root_note: MIDI note
        velocity: Note velocity

    Returns:
        List of pattern notes

    Examples:
        >>> create_odd_time_pattern((7, 8), "asymmetric", 60)  # 7/8 time
        # Could be grouped 3+2+2 or 2+2+3
    """
    numerator, denominator = time_signature
    beat_duration = 4 / denominator  # Assuming quarter note = 1 beat
    _total_duration = numerator * beat_duration  # noqa: kept for reference

    # Common groupings for odd meters
    groupings = {
        5: [[3, 2], [2, 3]],  # 5/4 or 5/8
        7: [[3, 2, 2], [2, 2, 3], [2, 3, 2]],  # 7/4 or 7/8
        9: [[3, 3, 3], [4, 3, 2], [2, 2, 2, 3]],  # 9/4 or 9/8
        11: [[3, 3, 3, 2], [4, 4, 3]],  # 11/4 or 11/8
        13: [[3, 3, 3, 4], [4, 3, 3, 3]],  # 13/4 or 13/8
    }

    if pattern_style == "asymmetric" and numerator in groupings:
        import random

        grouping = random.choice(groupings[numerator])
    else:
        grouping = [numerator]  # All beats grouped together

    return create_additive_rhythm(grouping, root_note, velocity)


def calculate_polyrhythm_grid(ratio: Tuple[int, int], resolution: int = 16) -> Dict:
    """
    Calculate a grid representation of a polyrhythm.

    Args:
        ratio: Tuple of (numerator, denominator)
        resolution: Grid resolution (default 16th notes)

    Returns:
        Dictionary with grid representation

    Examples:
        >>> calculate_polyrhythm_grid((3, 2), 16)
        {"layer1": [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0], "layer2": [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0]}
    """
    layer1_count, layer2_count = ratio

    # Calculate LCM for full cycle
    _lcm = abs(layer1_count * layer2_count) // math.gcd(layer1_count, layer2_count)  # noqa: kept for reference

    # Scale to resolution
    grid_size = resolution
    _layer1_interval = grid_size // layer1_count  # noqa: kept for reference
    _layer2_interval = grid_size // layer2_count  # noqa: kept for reference

    layer1_grid = [0] * grid_size
    layer2_grid = [0] * grid_size

    # Fill layer 1
    for i in range(layer1_count):
        pos = int((i / layer1_count) * grid_size)
        if pos < grid_size:
            layer1_grid[pos] = 1

    # Fill layer 2
    for i in range(layer2_count):
        pos = int((i / layer2_count) * grid_size)
        if pos < grid_size:
            layer2_grid[pos] = 1

    # Find coincidences (both layers hit)
    combined = [
        1 if (layer1_grid[i] and layer2_grid[i]) else 0 for i in range(grid_size)
    ]

    return {
        "layer1": layer1_grid,
        "layer2": layer2_grid,
        "combined": combined,
        "resolution": resolution,
    }


def visualize_polyrhythm(ratio: Tuple[int, int], width: int = 40) -> str:
    """
    Create a text visualization of a polyrhythm.

    Args:
        ratio: Tuple of (numerator, denominator)
        width: Character width of visualization

    Returns:
        String visualization

    Examples:
        >>> print(visualize_polyrhythm((3, 2)))
        Layer 1 (3): X----X----X----
        Layer 2 (2): X------X------
    """
    layer1_count, layer2_count = ratio
    grid = calculate_polyrhythm_grid(ratio, width)

    def grid_to_string(grid_list):
        return "".join("X" if x else "-" for x in grid_list)

    layer1_str = grid_to_string(grid["layer1"])
    layer2_str = grid_to_string(grid["layer2"])

    return f"Layer 1 ({layer1_count}): {layer1_str}\nLayer 2 ({layer2_count}): {layer2_str}"


def create_swing_pattern(
    pattern: List[int],
    swing_amount: float = 0.66,
    root_note: int = 60,
    velocity: int = 100,
) -> List[Dict]:
    """
    Apply swing to a rhythmic pattern.

    Args:
        pattern: List of beat subdivisions (1 = hit, 0 = rest)
        swing_amount: Swing percentage (0.5 = straight, 0.66 = triplet feel)
        root_note: MIDI note
        velocity: Note velocity

    Returns:
        List of swung notes

    Examples:
        >>> create_swing_pattern([1,0,1,0,1,0,1,0], 0.66, 60)  # Swung 8th notes
    """
    notes = []
    base_interval = 0.5  # 8th note interval

    for i, hit in enumerate(pattern):
        if hit:
            # Apply swing to off-beats
            if i % 2 == 1:  # Off-beat
                swing_offset = (swing_amount - 0.5) * base_interval
                start_time = i * base_interval + swing_offset
            else:  # On-beat
                start_time = i * base_interval

            notes.append(
                {
                    "pitch": root_note,
                    "start_time": start_time,
                    "duration": base_interval * 0.8,
                    "velocity": velocity,
                }
            )

    return notes


# Common polyrhythm presets
POLYRHYTHM_PRESETS = {
    "hemiola": (3, 2),
    "three_over_two": (3, 2),
    "four_over_three": (4, 3),
    "five_over_four": (5, 4),
    "five_over_three": (5, 3),
    "six_over_four": (6, 4),
    "seven_over_four": (7, 4),
    "seven_over_eight": (7, 8),
}


def create_preset_polyrhythm(
    preset_name: str,
    base_duration: float = 4.0,
    midi_notes: Optional[List[int]] = None,
    velocity: int = 100,
) -> List[Dict]:
    """
    Create a polyrhythm from a preset name.

    Args:
        preset_name: Name of preset ("hemiola", "four_over_three", etc.)
        base_duration: Total duration in beats
        midi_notes: MIDI notes for each layer
        velocity: Note velocity

    Returns:
        List of polyrhythm notes
    """
    preset_key = preset_name.lower().replace("-", "_").replace(" ", "_")

    if preset_key not in POLYRHYTHM_PRESETS:
        raise ValueError(
            f"Unknown preset: {preset_name}. Available: {list(POLYRHYTHM_PRESETS.keys())}"
        )

    ratio = POLYRHYTHM_PRESETS[preset_key]
    return create_polyrhythm(ratio, base_duration, midi_notes, velocity)


if __name__ == "__main__":
    # Test examples
    print("Polyrhythm Examples:")

    # 3:2 hemiola
    hemiola = create_polyrhythm((3, 2), 4, [60, 62])
    print(f"Hemiola (3:2): {len(hemiola)} notes")

    # Visualization
    print("\n" + visualize_polyrhythm((3, 2)))

    # Triplet
    triplet = create_triplet("8th", 3, 60)
    print(f"\nTriplet: {[n['start_time'] for n in triplet]}")

    # Quintuplet
    quint = create_quintuplet("8th", 60)
    print(f"Quintuplet: {[round(n['start_time'], 2) for n in quint]}")

    # Additive rhythm (3+3+2)
    additive = create_additive_rhythm([3, 3, 2], 60)
    print(f"\nAdditive (3+3+2): {len(additive)} notes")

    # 7/8 time pattern
    odd_time = create_odd_time_pattern((7, 8), "asymmetric", 60)
    print(f"\n7/8 pattern: {len(odd_time)} notes")

    # Grid calculation
    grid = calculate_polyrhythm_grid((3, 2), 16)
    print(
        f"\nGrid (3:2): Layer1 hits at {[i for i, v in enumerate(grid['layer1']) if v]}"
    )
