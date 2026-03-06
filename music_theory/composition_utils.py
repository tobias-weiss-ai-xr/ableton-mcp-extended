"""
Composition Utilities - Helper functions for music composition and arrangement.

This module provides utilities for generating musical ideas, variations,
and structural elements for electronic music production.
"""

from typing import List, Dict, Optional, Tuple
import random


# Standard arrangement section durations in bars
ARRANGEMENT_TEMPLATES = {
    "house": {
        "intro": 32,
        "build_1": 8,
        "drop_1": 16,
        "break_1": 16,
        "build_2": 8,
        "drop_2": 32,
        "break_2": 8,
        "build_3": 8,
        "drop_3": 32,
        "outro": 32,
    },
    "techno": {
        "intro": 64,
        "development": 32,
        "peak_1": 32,
        "break": 16,
        "peak_2": 48,
        "break_2": 8,
        "peak_3": 32,
        "outro": 32,
    },
    "dub_techno": {
        "intro": 64,
        "groove_1": 64,
        "evolution": 64,
        "peak": 64,
        "wind_down": 64,
    },
    "trance": {
        "intro": 32,
        "build_1": 16,
        "drop_1": 32,
        "break": 32,
        "build_2": 16,
        "drop_2": 64,
        "outro": 32,
    },
    "minimal": {
        "intro": 64,
        "groove": 128,
        "variation": 64,
        "outro": 64,
    },
}


def generate_melody(
    root_note: int,
    scale: str = "minor",
    length: int = 8,
    rhythm_density: float = 0.7,
    interval_range: Tuple[int, int] = (-7, 7),
    seed: Optional[int] = None,
) -> List[Dict]:
    """
    Generate a melody based on scale and rhythm parameters.

    Args:
        root_note: MIDI root note
        scale: Scale name (major, minor, dorian, etc.)
        length: Number of beats
        rhythm_density: Probability of note on each beat (0.0-1.0)
        interval_range: Min/max interval from root (semitones)
        seed: Random seed for reproducibility

    Returns:
        List of note dictionaries

    Examples:
        >>> generate_melody(60, "minor", 8, 0.7)
        [{"pitch": 60, "start_time": 0, "duration": 1, "velocity": 100}, ...]
    """
    if seed is not None:
        random.seed(seed)

    # Scale intervals
    scales = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "pentatonic_major": [0, 2, 4, 7, 9],
        "pentatonic_minor": [0, 3, 5, 7, 10],
        "blues": [0, 3, 5, 6, 7, 10],
    }

    scale_intervals = scales.get(scale, scales["minor"])

    # Generate scale notes within interval range
    available_notes = []
    for octave in range(-1, 2):
        for interval in scale_intervals:
            note = root_note + interval + (octave * 12)
            if interval_range[0] <= (interval + octave * 12) <= interval_range[1]:
                if 0 <= note <= 127:
                    available_notes.append(note)

    if not available_notes:
        available_notes = [root_note]

    notes = []
    current_note = root_note

    for beat in range(length):
        if random.random() < rhythm_density:
            # Choose note (prefer stepwise motion)
            if random.random() < 0.7:
                # Stepwise motion - pick adjacent note
                current_idx = (
                    available_notes.index(current_note)
                    if current_note in available_notes
                    else 0
                )
                step = random.choice([-1, 0, 1])
                new_idx = max(0, min(len(available_notes) - 1, current_idx + step))
                pitch = available_notes[new_idx]
                current_note = pitch
            else:
                # Leap - pick any note
                pitch = random.choice(available_notes)
                current_note = pitch

            # Duration (mostly 1 beat, some longer)
            duration = 1.0 if random.random() < 0.8 else 2.0

            # Velocity (slight variation)
            velocity = random.randint(85, 115)

            notes.append(
                {
                    "pitch": pitch,
                    "start_time": float(beat),
                    "duration": duration,
                    "velocity": velocity,
                }
            )

    return notes


def generate_bass_line(
    root_note: int,
    style: str = "root",
    length: int = 8,
    rhythm_pattern: Optional[List[int]] = None,
) -> List[Dict]:
    """
    Generate a bass line for a chord progression.

    Args:
        root_note: MIDI root note (will be transposed to bass range)
        style: Bass style ("root", "root_5", "walking", "arpeggio", "techno")
        length: Number of beats
        rhythm_pattern: Optional list of 1/0 for hits

    Returns:
        List of bass note dictionaries
    """
    # Transpose to bass range
    bass_root = max(36, min(48, root_note - 12))

    if rhythm_pattern is None:
        rhythm_pattern = [1] * length  # Every beat

    notes = []

    if style == "root":
        for i, hit in enumerate(rhythm_pattern):
            if hit:
                notes.append(
                    {
                        "pitch": bass_root,
                        "start_time": float(i),
                        "duration": 1.0,
                        "velocity": 100,
                    }
                )

    elif style == "root_5":
        for i, hit in enumerate(rhythm_pattern):
            if hit:
                pitch = bass_root if i % 4 < 2 else bass_root + 7
                notes.append(
                    {
                        "pitch": pitch,
                        "start_time": float(i),
                        "duration": 1.0,
                        "velocity": 100 if i % 4 == 0 else 85,
                    }
                )

    elif style == "walking":
        # Simple walking pattern
        chord_tones = [bass_root, bass_root + 4, bass_root + 7, bass_root + 12]
        for i, hit in enumerate(rhythm_pattern):
            if hit:
                notes.append(
                    {
                        "pitch": chord_tones[i % len(chord_tones)],
                        "start_time": float(i),
                        "duration": 1.0,
                        "velocity": 100 if i % 4 == 0 else 80,
                    }
                )

    elif style == "arpeggio":
        # Simple arpeggio
        arp_notes = [bass_root, bass_root + 7, bass_root + 12, bass_root + 7]
        for i, hit in enumerate(rhythm_pattern):
            if hit:
                notes.append(
                    {
                        "pitch": arp_notes[i % len(arp_notes)],
                        "start_time": float(i),
                        "duration": 0.8,
                        "velocity": 100,
                    }
                )

    elif style == "techno":
        # Offbeat techno bass
        for i, hit in enumerate(rhythm_pattern):
            if hit and i % 2 == 0:  # Only on beats 1 and 3
                notes.append(
                    {
                        "pitch": bass_root,
                        "start_time": float(i),
                        "duration": 0.5,
                        "velocity": 110,
                    }
                )

    return notes


def generate_arp_pattern(
    root_note: int,
    chord_type: str = "minor",
    pattern: str = "up",
    octaves: int = 2,
    rate: str = "8th",
    length: int = 8,
) -> List[Dict]:
    """
    Generate an arpeggio pattern.

    Args:
        root_note: MIDI root note
        chord_type: Chord type (major, minor, dim, aug, maj7, min7, dom7)
        pattern: Arp pattern ("up", "down", "updown", "random", "converge")
        octaves: Number of octaves to span
        rate: Note rate ("4th", "8th", "16th", "32nd")
        length: Total beats

    Returns:
        List of arp note dictionaries
    """
    # Chord intervals
    chords = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "dim": [0, 3, 6],
        "aug": [0, 4, 8],
        "maj7": [0, 4, 7, 11],
        "min7": [0, 3, 7, 10],
        "dom7": [0, 4, 7, 10],
        "sus2": [0, 2, 7],
        "sus4": [0, 5, 7],
    }

    intervals = chords.get(chord_type, chords["minor"])

    # Build chord across octaves
    arp_notes = []
    for oct in range(octaves):
        for interval in intervals:
            note = root_note + interval + (oct * 12)
            if 0 <= note <= 127:
                arp_notes.append(note)

    # Sort for up pattern
    arp_notes = sorted(set(arp_notes))

    # Rate to duration
    rate_durations = {
        "4th": 1.0,
        "8th": 0.5,
        "16th": 0.25,
        "32nd": 0.125,
    }
    duration = rate_durations.get(rate, 0.5)

    # Generate pattern
    notes = []
    beat = 0.0
    direction = 1
    current_idx = 0

    while beat < length:
        if pattern == "up":
            pitch = arp_notes[current_idx % len(arp_notes)]
            current_idx += 1
        elif pattern == "down":
            pitch = arp_notes[-(current_idx % len(arp_notes)) - 1]
            current_idx += 1
        elif pattern == "updown":
            pitch = arp_notes[current_idx % len(arp_notes)]
            if current_idx % len(arp_notes) == len(arp_notes) - 1:
                direction = -1
            elif current_idx % len(arp_notes) == 0:
                direction = 1
            current_idx += direction
        elif pattern == "random":
            pitch = random.choice(arp_notes)
        elif pattern == "converge":
            # Alternating low-high pattern
            if current_idx % 2 == 0:
                pitch = arp_notes[current_idx // 2 % len(arp_notes)]
            else:
                pitch = arp_notes[-(current_idx // 2) - 1 % len(arp_notes)]
            current_idx += 1
        else:
            pitch = arp_notes[current_idx % len(arp_notes)]
            current_idx += 1

        notes.append(
            {
                "pitch": pitch,
                "start_time": beat,
                "duration": duration * 0.9,
                "velocity": 90 + random.randint(-10, 10),
            }
        )

        beat += duration

    return notes


def generate_variation(
    original_notes: List[Dict],
    variation_type: str = "rhythm",
    intensity: float = 0.5,
) -> List[Dict]:
    """
    Create a variation of a melody or pattern.

    Args:
        original_notes: Original note list
        variation_type: Type of variation ("rhythm", "pitch", "velocity", "all")
        intensity: How much to vary (0.0-1.0)

    Returns:
        List of varied notes
    """
    varied_notes = []

    for note in original_notes:
        new_note = note.copy()

        if variation_type in ("pitch", "all"):
            if random.random() < intensity:
                # Vary pitch by small interval
                interval = random.choice([-2, -1, 1, 2])
                new_note["pitch"] = max(0, min(127, new_note["pitch"] + interval))

        if variation_type in ("rhythm", "all"):
            if random.random() < intensity:
                # Slight timing variation
                offset = random.uniform(-0.1, 0.1) * intensity
                new_note["start_time"] = max(0, new_note["start_time"] + offset)

        if variation_type in ("velocity", "all"):
            if random.random() < intensity:
                # Velocity variation
                variation = int(random.uniform(-20, 20) * intensity)
                new_note["velocity"] = max(
                    1, min(127, new_note["velocity"] + variation)
                )

        varied_notes.append(new_note)

    return varied_notes


def generate_call_response(
    call_notes: List[Dict],
    response_type: str = "echo",
    transpose: int = 0,
) -> List[Dict]:
    """
    Generate a response phrase to a call phrase.

    Args:
        call_notes: Original "call" phrase
        response_type: Type of response ("echo", "answer", "contrast", "sequence")
        transpose: Semitones to transpose

    Returns:
        List of response notes
    """
    if not call_notes:
        return []

    # Find the duration of the call phrase
    max_time = max(n["start_time"] + n["duration"] for n in call_notes)

    response_notes = []

    for note in call_notes:
        new_note = note.copy()
        new_note["start_time"] += max_time

        if response_type == "echo":
            # Exact repeat, maybe quieter
            new_note["velocity"] = int(new_note["velocity"] * 0.8)

        elif response_type == "answer":
            # Transpose up a 3rd or 5th
            new_note["pitch"] = min(
                127, new_note["pitch"] + random.choice([3, 4, 5, 7])
            )

        elif response_type == "contrast":
            # Invert direction roughly
            new_note["pitch"] = max(0, 127 - new_note["pitch"])

        elif response_type == "sequence":
            # Transpose by interval
            new_note["pitch"] = max(0, min(127, new_note["pitch"] + transpose))

        # Apply additional transpose
        if transpose != 0 and response_type != "sequence":
            new_note["pitch"] = max(0, min(127, new_note["pitch"] + transpose))

        response_notes.append(new_note)

    return response_notes


def get_arrangement_sections(template: str = "house") -> List[Dict]:
    """
    Get arrangement sections for a template.

    Args:
        template: Template name ("house", "techno", "dub_techno", "trance", "minimal")

    Returns:
        List of section dictionaries with name, start_bar, end_bar
    """
    sections_data = ARRANGEMENT_TEMPLATES.get(template, ARRANGEMENT_TEMPLATES["house"])

    sections = []
    current_bar = 0

    for name, bars in sections_data.items():
        sections.append(
            {
                "name": name,
                "start_bar": current_bar,
                "end_bar": current_bar + bars,
                "length_bars": bars,
            }
        )
        current_bar += bars

    return sections


def calculate_section_energy(section_name: str) -> float:
    """
    Calculate typical energy level for a section type.

    Args:
        section_name: Name of the section

    Returns:
        Energy level (0.0-1.0)
    """
    energy_levels = {
        "intro": 0.3,
        "build": 0.7,
        "build_1": 0.7,
        "build_2": 0.8,
        "build_3": 0.85,
        "drop": 0.95,
        "drop_1": 0.9,
        "drop_2": 0.95,
        "drop_3": 1.0,
        "break": 0.4,
        "break_1": 0.4,
        "break_2": 0.35,
        "outro": 0.2,
        "development": 0.6,
        "peak": 0.9,
        "peak_1": 0.85,
        "peak_2": 0.9,
        "peak_3": 0.95,
        "groove": 0.5,
        "groove_1": 0.5,
        "evolution": 0.65,
        "wind_down": 0.3,
        "variation": 0.55,
    }

    return energy_levels.get(section_name.lower(), 0.5)


def generate_fill(
    length: int = 1, density: float = 0.8, style: str = "snare"
) -> List[Dict]:
    """
    Generate a drum fill pattern.

    Args:
        length: Length in beats
        density: Note density (0.0-1.0)
        style: Fill style ("snare", "tom", "cymbal", "mixed")

    Returns:
        List of fill note dictionaries
    """
    # MIDI notes for drums
    drum_map = {
        "snare": 40,  # Snare
        "tom_high": 50,  # High Tom
        "tom_mid": 48,  # Mid Tom
        "tom_low": 45,  # Low Tom
        "cymbal": 49,  # Crash
        "hihat": 42,  # Closed Hi-hat
    }

    notes = []
    subdivisions = length * 4  # 16th notes

    for i in range(subdivisions):
        if random.random() < density:
            # Increase density toward end
            adjusted_density = density * (1 + (i / subdivisions) * 0.5)
            if random.random() < adjusted_density:
                if style == "snare":
                    pitch = drum_map["snare"]
                elif style == "tom":
                    pitch = random.choice(
                        [drum_map["tom_high"], drum_map["tom_mid"], drum_map["tom_low"]]
                    )
                elif style == "cymbal":
                    pitch = drum_map["cymbal"]
                elif style == "mixed":
                    pitch = random.choice(list(drum_map.values()))
                else:
                    pitch = drum_map["snare"]

                notes.append(
                    {
                        "pitch": pitch,
                        "start_time": i * 0.25,
                        "duration": 0.1,
                        "velocity": 80 + int(40 * (i / subdivisions)),
                    }
                )

    return notes


if __name__ == "__main__":
    # Test examples
    print("Composition Utilities Examples:")

    # Generate melody
    melody = generate_melody(60, "minor", 8, 0.7, seed=42)
    print(f"Generated melody: {len(melody)} notes")
    for note in melody[:4]:
        print(f"  Pitch: {note['pitch']}, Time: {note['start_time']}")

    # Generate bass
    bass = generate_bass_line(48, "root_5", 8)
    print(f"\nGenerated bass: {len(bass)} notes")

    # Generate arp
    arp = generate_arp_pattern(60, "minor", "up", 2, "8th", 4)
    print(f"\nGenerated arp: {len(arp)} notes")

    # Get arrangement
    sections = get_arrangement_sections("house")
    print(
        f"\nHouse arrangement: {len(sections)} sections, {sections[-1]['end_bar']} bars total"
    )

    # Generate fill
    fill = generate_fill(2, 0.7, "snare")
    print(f"\nGenerated fill: {len(fill)} notes")
