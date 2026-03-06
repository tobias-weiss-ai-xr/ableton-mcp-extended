# Rhythm Theory Reference

> Drum patterns, grid notation, syncopation, polyrhythms, and electronic music rhythm theory

---

## Grid Notation System

### 16th Note Grid (4/4)

```
Beat:    1     &     2     &     3     &     4     &
Grid:    |-----|-----|-----|-----|-----|-----|-----|
Slots:   1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16
```

### Pattern Representation

| Symbol | Meaning |
|--------|---------|
| `X` | Hit (note on) |
| `-` | Rest (note off) |
| `x` | Ghost note (quiet hit) |
| `>` | Accent (loud hit) |

### Example: Basic 4/4 Kick

```
Kick:   X---X---X---X---
        1   2   3   4
```

---

## Drum Kit Reference

### Standard MIDI Mapping (GM)

| Sound | MIDI Note | Common Use |
|-------|-----------|------------|
| **Kick** | 36 (C1) | Bass drum, downbeat |
| **Snare** | 38 (D1) / 40 (E1) | Backbeat (2 & 4) |
| **Hi-Hat Closed** | 42 (F#1) | Timekeeping |
| **Hi-Hat Open** | 46 (A#1) | Transitions |
| **Clap** | 39 (D#1) | House, techno |
| **Rim** | 37 (C#1) / 41 (F1) | Reggae, dub |
| **Tom High** | 50 (D2) | Fills |
| **Tom Mid** | 48 (C2) | Fills |
| **Tom Low** | 45 (A1) | Fills |
| **Crash** | 49 (C#2) | Transitions, accents |
| **Ride** | 51 (D#2) | Jazz, variation |
| **Cowbell** | 56 (G#2) | Latin, disco |

### Alternative Mappings

**Roland TR-808/909:**
| Sound | MIDI Note |
|-------|-----------|
| Kick | 36 |
| Snare | 38 |
| Clap | 39 |
| Hat Closed | 42 |
| Hat Open | 46 |
| Rim | 37 |

---

## Basic Patterns

### 4/4 Kick Patterns

#### Straight 4/4 (House, Techno)

```
Kick:   X---X---X---X---
        1   2   3   4

MIDI:   [36@0.0, 36@1.0, 36@2.0, 36@3.0]
```

#### Syncopated Kick (Dub Techno)

```
Kick:   X-----X-X---X---
        1   2   3   4

MIDI:   [36@0.0, 36@1.5, 36@2.0, 36@3.0]
```

#### Offbeat Kick (Broken Beat)

```
Kick:   --X---X---X---X-
        1   2   3   4

MIDI:   [36@0.5, 36@1.5, 36@2.5, 36@3.5]
```

### Snare/Clap Patterns

#### Backbeat (2 & 4)

```
Snare:  ----X-------X---
        1   2   3   4

MIDI:   [38@1.0, 38@3.0]
```

#### Double Backbeat

```
Snare:  ----X-X-----X-X-
        1   2   3   4

MIDI:   [38@1.0, 38@1.5, 38@3.0, 38@3.5]
```

### Hi-Hat Patterns

#### 8th Notes

```
Hat:    X---X---X---X---X---X---X---X---
        1       2       3       4

MIDI:   [42@0.0, 42@0.5, 42@1.0, ...]
```

#### 16th Notes

```
Hat:    X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-
        1 & 2 & 3 & 4 &

MIDI:   [42@0.0, 42@0.25, 42@0.5, ...]
```

#### Offbeat (Disco/House)

```
Hat:    ----X-------X-------X-------X-
        1   &   2   &   3   &   4   &

MIDI:   [42@0.5, 42@1.5, 42@2.5, 42@3.5]
```

---

## Genre Patterns

### House

#### Basic House

```
Kick:   X---X---X---X---
Clap:   ----X-------X---
Hat:    ----X-------X--- (open)
Hat:    X-X-X-X-X-X-X-X- (closed)

MIDI:
Kick:  [36@0, 36@1, 36@2, 36@3]
Clap:  [39@1, 39@3]
Hat:   [42@0.0, 42@0.25, 42@0.5, 42@0.75, ...]
```

#### Deep House

```
Kick:   X---X---X---X---
Clap:   ----X-------X---
Hat:    ----X-------X--- (open)
Rim:    X-X-----X-X-----

MIDI:
Kick:  [36@0, 36@1, 36@2, 36@3]
Clap:  [39@1, 39@3]
Hat:   [46@0.5, 46@1.5, 46@2.5, 46@3.5]
Rim:   [37@0.0, 37@0.25, 37@1.0, 37@1.25]
```

**MCP Command:**
```python
create_drum_pattern(
    track_index=0, clip_index=0,
    pattern_name="house_basic",
    length=4
)
```

### Techno

#### Driving Techno

```
Kick:   X---X---X---X---
Hat:    --X---X---X---X-
Clap:   ----X-------X---

MIDI:
Kick:  [36@0, 36@1, 36@2, 36@3]
Hat:   [42@0.5, 42@1.5, 42@2.5, 42@3.5]
Clap:  [39@1, 39@3]
```

#### Minimal Techno

```
Kick:   X-------X---X---
Hat:    X---X---X---X---
Clap:   --------X-------

MIDI:
Kick:  [36@0, 36@2, 36@3]
Hat:   [42@0, 42@1, 42@2, 42@3]
Clap:  [39@2]
```

### Dub Techno

#### One Drop

```
Kick:   X---------X-----
Snare:  ----X-----------
Hat:    X-X-X-X-X-X-X-X-

MIDI:
Kick:  [36@0, 36@2.5]
Snare: [38@1]
Hat:   [42@0.0, 42@0.25, 42@0.5, 42@0.75, ...]
```

**MCP Command:**
```python
create_drum_pattern(
    track_index=0, clip_index=0,
    pattern_name="one_drop",
    length=4
)
```

#### Steppers

```
Kick:   X-X-X-X-X-X-X-X-
Snare:  ----X-------X---
Hat:    X-X-X-X-X-X-X-X-

MIDI:
Kick:  [36@0, 36@0.5, 36@1, 36@1.5, 36@2, 36@2.5, 36@3, 36@3.5]
Snare: [38@1, 38@3]
Hat:   [42@0.0, 42@0.25, 42@0.5, 42@0.75, ...]
```

#### Rockers

```
Kick:   X---X-----X-X---
Snare:  ----X-------X---
Hat:    X-X-X-X-X-X-X-X-

MIDI:
Kick:  [36@0, 36@1, 36@2, 36@2.5, 36@3]
Snare: [38@1, 38@3]
Hat:   [42@0.0, 42@0.25, 42@0.5, 42@0.75, ...]
```

### Reggae

#### Skank (Guitar/Keys)

```
Chord:  X-----X-X-----X-
        1   2   3   4

(on beats 2 and 4, with anticipation)
```

#### Reggae Drums

```
Kick:   X---------X-----
Snare:  ----X-------X---
Rim:    X-X-----X-X-----
Hat:    X-X-X-X-X-X-X-X-

MIDI:
Kick:  [36@0, 36@2.5]
Snare: [38@1, 38@3]
Rim:   [37@0, 37@0.25, 37@1, 37@1.25]
Hat:   [42@0.0, 42@0.25, 42@0.5, 42@0.75, ...]
```

### Drum & Bass

#### Amen Break Style

```
Kick:   X-----X-X---X-X-
Snare:  ----X-------X---
Hat:    X-X-X-X-X-X-X-X-

MIDI:
Kick:  [36@0, 36@1.5, 36@2, 36@3, 36@3.5]
Snare: [38@1, 38@3]
Hat:   [42@0.0, 42@0.25, 42@0.5, 42@0.75, ...]
```

### Hip-Hop

#### Boom Bap

```
Kick:   X-------X---X---
Snare:  ----X-------X---
Hat:    X-X-X-X-X-X-X-X-

MIDI:
Kick:  [36@0, 36@2, 36@3]
Snare: [38@1, 38@3]
Hat:   [42@0.0, 42@0.25, 42@0.5, 42@0.75, ...]
```

#### Trap

```
Kick:   X---------X-X---
Snare:  ----X-------X---
Hat:    XXXXXXXXXXXXXXXX (rapid 16ths or 32nds)
808:    X---------X-X--- (sustained bass)

MIDI:
Kick:  [36@0, 36@2.5, 36@3]
Snare: [38@1, 38@3]
Hat:   [42@0.0, 42@0.125, 42@0.25, ...]
```

---

## Polyrhythm Theory

### What Is Polyrhythm?

**Definition:** Two or more rhythms played simultaneously with different beat divisions.

**Common Ratios:**
- 3:2 (hemiola)
- 3:4
- 5:4
- 7:8

### 3:2 Polyrhythm (Hemiola)

```
Layer 1 (3):  X--X--X--
Layer 2 (2):  X---X---

Combined:
Beat 1: X (both)
Beat 2: X (layer 1)
Beat 3: X (layer 2)
Beat 4: X (layer 1)
Beat 5: X (layer 1)
Beat 6: X (both)

Grid:   X-X-XX-X
```

**MCP Usage:**
```python
from music_theory.polyrhythm import create_polyrhythm

# 3:2 polyrhythm
notes = create_polyrhythm(
    ratio=(3, 2),
    base_duration=4,  # 4 beats total
    midi_notes=[60, 62]  # Two different pitches
)
```

### 3:4 Polyrhythm

```
Layer 1 (3):  X----X----X----
Layer 2 (4):  X--X--X--X--X--

Combined timing:
0.00: X (both)
1.00: X (layer 2)
1.33: X (layer 1)
2.00: X (layer 2)
2.67: X (layer 1)
3.00: X (layer 2)
4.00: X (both)
```

### 5:4 Polyrhythm

```
Layer 1 (5):  X---X---X---X---X---
Layer 2 (4):  X----X----X----X----

Used in progressive metal, math rock
```

---

## Tuplets

### Triplets

**Definition:** 3 notes in the time of 2

```
8th Note Triplets:
Grid:   X-X-X-X-X-X-X-X-X-X-X-X-
Beat:   1     2     3     4
Triplets: 1 & a 2 & a 3 & a 4 & a

MIDI Timing:
[0.0, 0.333, 0.667, 1.0, 1.333, 1.667, ...]
```

### Quarter Note Triplets

```
3 quarter notes in 2 beats:
Grid:   X-----X-----X-----
Beat:   1           2

MIDI Timing:
[0.0, 0.667, 1.333]
```

### Quintuplets (5:4)

```
5 notes in 1 beat:
Grid:   X-X-X-X-X-
Beat:   1

MIDI Timing:
[0.0, 0.2, 0.4, 0.6, 0.8]
```

---

## Syncopation

### Definition

**Syncopation:** Placing emphasis on weak beats or offbeats

### Types of Syncopation

#### 1. Offbeat Syncopation

```
Normal:    X---X---X---X---
Syncopated: --X---X---X---X-

Emphasis shifted to "&" beats
```

#### 2. Anticipation

```
Normal:    X-------X-------
Anticipated: X-----X-X-------

Chord arrives early (on 4&)
```

#### 3. Suspension

```
Normal:    X-------X-------
Sustained: X-------------X-

Note holds past expected release
```

#### 4. Backbeat Displacement

```
Normal:    ----X-------X--- (snare on 2 & 4)
Displaced: --X---------X--- (snare on 1& and 3&)
```

### Syncopation in Electronic Music

**House:** Offbeat hi-hats, anticipated claps
**Techno:** Syncopated kick patterns
**Dub:** Heavy use of space and anticipation
**DnB:** Breakbeat syncopation

---

## Swing & Groove

### Straight vs Swing

**Straight:**
```
X---X---X---X---
Equal spacing
```

**Swing:**
```
X--X--X--X--X--X-
Long-short pattern
```

### Swing Percentages

| Percentage | Feel | Genre |
|------------|------|-------|
| 50% | Straight | Techno, House |
| 55% | Light swing | Deep House |
| 60% | Medium swing | Hip-Hop |
| 66% | Triplet feel | Jazz, Blues |
| 70% | Heavy swing | Jazz, Funk |

### Swing in Grid Notation

```
Straight 8ths:
Beat:    1     2     3     4
Grid:    X---X---X---X---
Time:    0.0 0.5 1.0 1.5

Swing 8ths (66%):
Beat:    1     2     3     4
Grid:    X--X--X--X--X--X--
Time:    0.0 0.66 1.0 1.66

The "&" is delayed
```

---

## Tempo Ranges

### BPM by Genre

| Genre | BPM Range | Typical |
|-------|-----------|---------|
| **Dub** | 60-80 | 70-75 |
| **Hip-Hop** | 80-100 | 90 |
| **House** | 115-130 | 125-128 |
| **Deep House** | 115-125 | 120-122 |
| **Techno** | 125-145 | 130-138 |
| **Dub Techno** | 110-130 | 120-126 |
| **Trance** | 125-150 | 138 |
| **Drum & Bass** | 160-180 | 174 |
| **Dubstep** | 135-145 | 140 |

### Tempo Relationships

**Double-time / Half-time:**
- 70 BPM = 140 BPM (dubstep at half-time feels like dub)
- 87 BPM = 174 BPM (hip-hop double-time = DnB)

**MCP Command:**
```python
set_tempo(126)  # Set to 126 BPM
```

---

## Fills & Transitions

### Basic Fills

#### End-of-Bar Fill

```
Bar 1-3: Normal pattern
Bar 4:   X-X-X-X-X-X-X-X- (16th note fill)

Kick:   X---X---X---X-X-
Snare:  ----X-------X-X-
Hat:    X-X-X-X-X-X-X-X-
```

#### 2-Bar Fill

```
Bar 3:  X---X---X---X---
Bar 4:  X-X-X-X-XXXXXXXX (crescendo)

Kick:   X---X---X---X-X-
Snare:  ----X-------X-X-
Toms:   --------X-X-X-X-
```

### Transition Patterns

#### Snare Roll Build

```
Bar 1:  ----X-------X---
Bar 2:  ----X-X-----X-X-
Bar 3:  ----X-X-X-X-X-X-
Bar 4:  XXXXXXXXXXXXXXXX

Gradual increase in density
```

#### Hat Open Build

```
Bar 1:  ----X-------X--- (closed)
Bar 2:  ----X-------X--- (half-open)
Bar 3:  ----X-------X--- (open)
Bar 4:  X-X-X-X-X-X-X-X- (crash + open hat)
```

---

## Ghost Notes

### Definition

**Ghost Note:** A quiet note played between main beats, adds groove

### Ghost Note Patterns

```
Main:   X---X---X---X---
Ghost:  -x-x-x-x-x-x-x-x-
Combined:X-x-X-x-X-x-X-x-

The 'x' notes are played much quieter (velocity 20-40)
```

### Funk Ghost Pattern

```
Kick:   X-------X---X---
Snare:  ----X-------X---
Ghost:  -x-x-x-x-x-x-x-x-
Hat:    X-X-X-X-X-X-X-X-

MIDI Velocities:
Kick:  127, 127, 127
Snare: 127, 127
Ghost: 30-50
Hat:   80-100
```

---

## MCP Integration

### Create Drum Pattern

```python
# House pattern
create_drum_pattern(
    track_index=0,
    clip_index=0,
    pattern_name="house_basic",
    length=4,
    kick_note=36,
    snare_note=40,
    hat_note=42,
    clap_note=39
)
```

### Available Patterns

| Pattern Name | Genre | Character |
|--------------|-------|-----------|
| `one_drop` | Reggae/Dub | Roots feel |
| `rockers` | Reggae | Upbeat |
| `steppers` | Reggae/Dub | Driving 4/4 |
| `house_basic` | House | Standard 4/4 |
| `techno_4x4` | Techno | Driving, minimal |
| `dub_techno` | Dub Techno | Syncopated |

### Add Custom Pattern

```python
# Custom drum pattern
notes = []

# Kick on 1, 2, 3, 4
notes.append({"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 127})
notes.append({"pitch": 36, "start_time": 1.0, "duration": 0.25, "velocity": 127})
notes.append({"pitch": 36, "start_time": 2.0, "duration": 0.25, "velocity": 127})
notes.append({"pitch": 36, "start_time": 3.0, "duration": 0.25, "velocity": 127})

# Snare on 2, 4
notes.append({"pitch": 38, "start_time": 1.0, "duration": 0.25, "velocity": 127})
notes.append({"pitch": 38, "start_time": 3.0, "duration": 0.25, "velocity": 127})

# Hi-hats on 8th notes
for i in range(8):
    notes.append({"pitch": 42, "start_time": i * 0.5, "duration": 0.25, "velocity": 80})

add_notes_to_clip(track_index=0, clip_index=0, notes=notes)
```

### Create Polyrhythm (Requires polyrhythm.py)

```python
from music_theory.polyrhythm import create_polyrhythm

# 3:2 polyrhythm across 4 beats
notes = create_polyrhythm(
    ratio=(3, 2),
    base_duration=4,
    midi_notes=[60, 62],
    velocity=100
)
add_notes_to_clip(track_index=0, clip_index=0, notes=notes)
```

---

## Practice Exercises

### Exercise 1: Pattern Recognition

Identify the pattern:
```
Kick:   X---X---X---X---
Snare:  ----X-------X---
Hat:    X-X-X-X-X-X-X-X-
```

<details>
<summary>Answer</summary>
Basic house/techno pattern
</details>

### Exercise 2: Create Syncopation

Add syncopation to this pattern:
```
Original: X---X---X---X---
```

<details>
<summary>Suggested Answer</summary>
```
Syncopated: X-----X-X---X---
or
Syncopated: --X---X---X---X-
```
</details>

### Exercise 3: Fill Construction

Create a 1-bar fill leading to chorus:
```
Bar 4 (fill): ________________
```

<details>
<summary>Suggested Answer</summary>
```
Kick:   X---X---X-X-X-X-
Snare:  ----X-X-X-X-X-X-
Hat:    X-X-X-X-X-X-X-X-
Crash:  X---------------
```
</details>

---

## Quick Reference Cards

### House Pattern Card

```
Kick:   X---X---X---X---
Clap:   ----X-------X---
Hat:    X-X-X-X-X-X-X-X-
Hat(O): ----X-------X---
```

### Techno Pattern Card

```
Kick:   X---X---X---X---
Hat:    --X---X---X---X-
Clap:   ----X-------X---
```

### Dub/Reggae Pattern Card

```
Kick:   X---------X-----
Snare:  ----X-------X---
Hat:    X-X-X-X-X-X-X-X-
Rim:    X-X-----X-X-----
```

### DnB Pattern Card

```
Kick:   X-----X-X---X-X-
Snare:  ----X-------X---
Hat:    X-X-X-X-X-X-X-X-
```

---

## Further Reading

- **genre_theory.md** - Genre-specific rhythm applications
- **polyrhythm.py** - Polyrhythm generation code
- **arpeggiator.py** - Rhythmic arpeggiation

---

*Last updated: 2026-03-03*
