# Music Theory Reference

> Comprehensive music theory resources for electronic music production with Ableton MCP

---

## Overview

This folder contains music theory documentation and Python utilities for the Ableton MCP Extended project. It covers scales, chords, progressions, rhythm, harmonic mixing, and genre-specific theory.

---

## Documentation Files

### Core Theory

| File | Description | Contents |
|------|-------------|----------|
| **[scales.md](scales.md)** | Scale reference | Diatonic scales, modes, pentatonic, exotic scales, usage examples |
| **[chords.md](chords.md)** | Chord reference | Triads, 7ths, extended chords, voicings, substitutions |
| **[progressions.md](progressions.md)** | Chord progressions | Pop, rock, jazz, blues, electronic progressions with Roman numerals |
| **[rhythm.md](rhythm.md)** | Rhythm theory | Drum patterns, grid notation, syncopation, polyrhythms |
| **[harmonic_mixing.md](harmonic_mixing.md)** | DJ theory | Camelot wheel, key transitions, energy management |

### Genre-Specific

| File | Description | Contents |
|------|-------------|----------|
| **[genre_theory.md](genre_theory.md)** | Genre deep dives | Dub techno, house, techno, reggae, trance, DnB, hip-hop |

### Advanced Topics

| File | Description | Contents |
|------|-------------|----------|
| **[modes.md](modes.md)** | Modal theory | Mode characteristics, modal interchange |
| **[voice_leading.md](voice_leading.md)** | Voice leading | Smooth transitions, inversions, bass motion |

---

## Python Modules

### Core Modules

| Module | Description | Key Functions |
|--------|-------------|---------------|
| **[chord.py](chord.py)** | Chord naming | `generate_chord_name()` |
| **[progression.py](progression.py)** | Progression analysis | `analyze_progression()` |
| **[voicing.py](voicing.py)** | Voicing generation | `generate_voicing()`, `VOICING_TEMPLATES` |
| **[arpeggiator.py](arpeggiator.py)** | Arpeggiation | `arpeggiate_chord()` |
| **[grid.py](grid.py)** | Controller layouts | `generate_camelot_grid()`, `generate_chromatic_grid()` |

### Extended Modules

| Module | Description | Key Functions |
|--------|-------------|---------------|
| **[extensions.py](extensions.py)** | Extended chords | `create_extended_chord()`, `create_altered_chord()`, `suggest_extension()` |
| **[exotic_scales.py](exotic_scales.py)** | Exotic scales | `generate_exotic_scale_notes()`, `suggest_chords_for_exotic_scale()` |
| **[harmonization.py](harmonization.py)** | Harmonization | `harmonize_melody()`, `suggest_chords_for_melody()`, `detect_key_from_chords()` |
| **[polyrhythm.py](polyrhythm.py)** | Polyrhythms | `create_polyrhythm()`, `create_triplet()`, `create_additive_rhythm()` |

---

## Quick Reference

### Scales

```python
# Available in MCP server
scales = ["major", "minor", "dorian", "phrygian", "lydian", 
          "mixolydian", "pentatonic_major", "pentatonic_minor", "blues"]

# In exotic_scales.py
exotic = ["harmonic_minor", "melodic_minor", "whole_tone", 
          "diminished", "double_harmonic", "hungarian_minor"]
```

### Chords

```python
# Basic chords
basic = ["major", "minor", "dim", "aug", "sus2", "sus4", "power"]

# 7th chords
sevenths = ["maj7", "min7", "dom7", "dim7", "m7b5"]

# Extended chords (in extensions.py)
extended = ["maj9", "min9", "dom9", "min11", "dom13"]

# Altered dominants
altered = ["7b5", "7#5", "7b9", "7#9", "7#5b9", "7#5#9"]
```

### Drum Patterns

```python
# Available patterns
patterns = ["one_drop", "rockers", "steppers", 
            "house_basic", "techno_4x4", "dub_techno"]
```

---

## MCP Integration Examples

### Create Scale Clip

```python
# Create C minor scale reference clip (for Fold function)
create_scale_reference_clip(
    track_index=0,
    clip_index=0,
    scale="minor",
    root=60,  # C4
    octaves=3
)
```

### Create Chord Progression

```python
# ii-V-I in C major
create_chord_progression(
    track_index=0,
    clip_index=0,
    key="C",
    progression=["ii", "V", "I"],
    duration_per_chord=4
)

# Dub techno progression
create_chord_progression(
    track_index=0,
    clip_index=0,
    key="Am",
    progression=["i", "VII", "VI", "V"],
    duration_per_chord=8
)
```

### Create Drum Pattern

```python
# House pattern
create_drum_pattern(
    track_index=0,
    clip_index=0,
    pattern_name="house_basic",
    length=4
)

# Dub reggae pattern
create_drum_pattern(
    track_index=0,
    clip_index=0,
    pattern_name="one_drop",
    length=4
)
```

### Harmonic Mixing

```python
# Get compatible keys for A minor (8A)
get_compatible_keys("8A")
# Returns: {"one_up": "9A", "one_down": "7A", "relative": "8B"}

# Suggest key transition
suggest_key_transition("8A", "up")
# Returns: {"target": "9A", "semitones": 1, "energy_change": "slight boost"}

# Detect key from clip
detect_clip_key(track_index=0, clip_index=0)
# Returns: {"key": "A minor", "camelot": "8A", "confidence": 0.85}
```

### Extended Chords (Python Module)

```python
from music_theory.extensions import create_extended_chord, create_altered_chord

# Create minor 11 chord
notes = create_extended_chord(60, "min11")
# Returns: [60, 63, 67, 70, 74, 77]  # C-Eb-G-Bb-D-F

# Create Hendrix chord (C7#9)
notes = create_altered_chord(60, ["#9"])
# Returns: [60, 64, 67, 70, 75]  # C-E-G-Bb-D#

# Rootless voicing
notes = create_extended_chord(60, "min11", voicing="rootless_11")
# Returns: [67, 70, 74, 77]  # G-Bb-D-F
```

### Polyrhythms (Python Module)

```python
from music_theory.polyrhythm import create_polyrhythm, create_triplet

# 3:2 polyrhythm
notes = create_polyrhythm((3, 2), base_duration=4, midi_notes=[60, 62])

# 8th note triplet
notes = create_triplet("8th", count=3, root_note=60)
```

### Harmonization (Python Module)

```python
from music_theory.harmonization import harmonize_melody, suggest_chords_for_melody

# Harmonize a melody
melody = [60, 64, 67, 72]  # C-E-G-C
chords = harmonize_melody(melody, key_root=60, scale="major")

# Get chord suggestions
suggestions = suggest_chords_for_melody([60, 64], key_root=60, scale="major")
```

---

## Scale Quick Reference

| Scale | Intervals | Character | Best For |
|-------|-----------|-----------|----------|
| Major | 0-2-4-5-7-9-11 | Bright, happy | Pop, trance |
| Minor | 0-2-3-5-7-8-10 | Dark, melancholic | Techno, dub |
| Dorian | 0-2-3-5-7-9-10 | Soulful, minor with lift | House, jazz |
| Phrygian | 0-1-3-5-7-8-10 | Spanish, dark | Techno, metal |
| Lydian | 0-2-4-6-7-9-11 | Dreamy, floating | Ambient, film |
| Mixolydian | 0-2-4-5-7-9-10 | Bluesy, rock | Blues, rock |
| Pentatonic Major | 0-2-4-7-9 | Universal, open | Pop, folk |
| Pentatonic Minor | 0-3-5-7-10 | Bluesy, rock | Blues, rock |
| Blues | 0-3-5-6-7-10 | Soulful, expressive | Blues, jazz |

---

## Chord Quick Reference

### Basic Chords

| Chord | Intervals | Symbol | Character |
|-------|-----------|--------|-----------|
| Major | 0-4-7 | C | Bright |
| Minor | 0-3-7 | Cm | Dark |
| Diminished | 0-3-6 | Cdim | Tense |
| Augmented | 0-4-8 | Caug | Dreamy |
| Sus2 | 0-2-7 | Csus2 | Open |
| Sus4 | 0-5-7 | Csus4 | Tense |
| Power | 0-7 | C5 | Heavy |

### 7th Chords

| Chord | Intervals | Symbol | Character |
|-------|-----------|--------|-----------|
| Major 7 | 0-4-7-11 | Cmaj7 | Jazzy |
| Minor 7 | 0-3-7-10 | Cm7 | Smooth |
| Dominant 7 | 0-4-7-10 | C7 | Bluesy |
| Diminished 7 | 0-3-6-9 | Cdim7 | Cinematic |

---

## Tempo Reference

| Genre | BPM Range | Typical |
|-------|-----------|---------|
| Dub | 60-80 | 70-75 |
| Hip-Hop | 80-100 | 90 |
| House | 115-130 | 125-128 |
| Deep House | 115-125 | 120-122 |
| Techno | 125-145 | 130-138 |
| Dub Techno | 110-130 | 120-126 |
| Trance | 125-150 | 138 |
| Drum & Bass | 160-180 | 174 |

---

## Contributing

To add new theory content:

1. **Documentation**: Create new `.md` files with clear sections
2. **Code**: Create new `.py` modules with docstrings
3. **Integration**: Add MCP commands in `server.py` if needed
4. **Testing**: Add tests in `tests/test_music_theory_tools.py`

---

## External Resources

- **Mixed In Key**: https://mixedinkey.com/ (Camelot Wheel)
- **Hooktheory**: https://www.hooktheory.com/ (Chord Progressions)
- **Attack Magazine**: https://www.attackmagazine.com/ (Drum Patterns)
- **Teoria**: https://teoria.com/ (Music Theory Reference)

---

*Last updated: 2026-03-03*
