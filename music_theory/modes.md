# Modes Reference Guide

> Deep dive into modal theory, mode characteristics, and modal interchange

---

## What Are Modes?

**Modes** are scales derived from a parent scale by starting on a different note while using the same notes.

**Example:** C Major = C-D-E-F-G-A-B

| Mode | Notes | Starting From |
|------|-------|----------------|
| **C Ionian** | C-D-E-F-G-A-B | C Major (root position) |
| **D Dorian** | D-E-F-G-A-B-C | C Major (2nd mode) |
| **E Phrygian** | E-F-G-A-B-C-D | C Major (3rd mode) |
| **F Lydian** | F-G-A-B-C-D-E | C Major (4th mode) |
| **G Mixolydian** | G-A-B-C-D-E-F | C Major (5th mode) |
| **A Aeolian** | A-B-C-D-E-F-G | C Major (6th mode) |
| **B Locrian** | B-C-D-E-F-G-A | C Major (7th mode) |

---

## The Seven Modes of Major

### 1. Ionian (Major Scale)

**Intervals:** `0-2-4-5-7-9-11` (W-W-H-W-W-W-H)

**Notes in C Ionian:** C - D - E - F - G - A - B

**Character:**
- Bright, happy, resolved
- Most familiar scale
- Foundation of Western tonality

**Chord Quality:** Major (I)

**Relative Modes:**
- Dorian: a half step up
- Mixolydian: a fourth up
- Lydian: a fourth up

**Best For:** Pop, classical, bright melodies

**Famous Songs:**
- "Happy Birthday"
- "Twinkle Twinkle Little Star"
- Most pop/rock songs

---

### 2. Dorian Mode

**Intervals:** `0-2-3-5-7-9-10` (W-H-W-W-W-H-W)

**Notes in D Dorian:** D - E - F - G - A - B - C

**Character:**
- Soulful, minor with brightness
- Minor 3rd + Major 6th
- Jazz, funk, house music

**Chord Quality:** Minor (ii)

**The "Dorian" Sound:**
- The major 6th (B in D Dorian) is the key difference from natural minor
- Creates a "brighter" minor sound
- Works over minor 7th chords

**Best For:** Funk, house, jazz, fusion

**Famous Songs:**
- "So What" - Miles Davis
- "Oye Como Va" - Tito Puente
- "Get Lucky" - Daft Punk
- "Billie Jean" - Michael Jackson

**MCP Usage:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="dorian", root=62)
```

---

### 3. Phrygian Mode

**Intervals:** `0-1-3-5-7-8-10` (H-W-W-W-H-W-W)

**Notes in E Phrygian:** E - F - G - A - B - C - D

**Character:**
- Spanish, exotic, dark
- Minor 2nd creates tension
- Flamenco, metal, film scores

**Chord Quality:** Minor (iii)

**The "Phrygian" Sound:**
- The minor 2nd (F in E Phrygian) creates "Spanish" sound
- Darker than natural minor
- Tension without resolution

**Best For:** Flamenco, metal, film scores, techno

**Famous Songs:**
- "White Rabbit" - Jefferson Airplane
- Spanish flamenco music
- Metal intros and riffs

**Phrygian Dominant (Spanish Gypsy):**
- 5th mode of harmonic minor
- Intervals: `0-1-4-5-7-8-10`
- Major 3rd + minor 2nd = Spanish sound

**MCP Usage:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="phrygian", root=64)
```

---

### 4. Lydian Mode

**Intervals:** `0-2-4-6-7-9-11` (W-W-W-H-W-W-H)

**Notes in F Lydian:** F - G - A - B - C - D - E

**Character:**
- Dreamy, floating, ethereal
- Sharp 4th creates "lifting" sensation
- Film scores, ambient. progressive rock

**Chord Quality:** Major (IV)

**The "Lydian" Sound:**
- The augmented 4th (B in F Lydian) = "The Simpson's sound"
- No avoid notes (all notes sound good)
- Resolves to itself

**Best For:** Film scores, ambient. progressive rock, dream sequences

**Famous Songs:**
- "Flying in a Blue Dream" - Joe Satriani
- "Dreams" - Fleetwood Mac
- "The Simpson's Theme"
- Film scores (Hans Zimmer)

**Why It Works:**
- No tritone with root (unlike major)
- Sharp 4th creates tension that never fully resolves
- "Floating" quality

**MCP Usage:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="lydian", root=65)
```

---

### 5. Mixolydian Mode

**Intervals:** `0-2-4-5-7-9-10` (W-W-H-W-W-H-W)

**Notes in G Mixolydian:** G - A - B - C - D - E - F

**Character:**
- Bluesy, rock-oriented
- Major with flat 7
- Blues, rock, funk. jam bands

**Chord Quality:** Dominant (V)

**The "Mixolydian" Sound:**
- The minor 7th (F in G Mixolydian) = dominant quality
- Works over dominant 7th chords
- Foundation for blues improvisation

**Best For:** Blues, rock. funk. jam bands

**Famous Songs:**
- "Sweet Child O' Mine" - Guns N' Roses
- "Sweet Home Alabama" - Lynyrd Skynyrd
- "Hey Jude" - The Beatles
- "Born Under a Bad Sign" - Albert King

**Dominant Chord Scale:**
- G Mixolydian = G7 scale
- Works over any dominant 7th chord

**MCP Usage:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="mixolydian", root=67)
```

---

### 6. Aeolian Mode (Natural Minor)

**Intervals:** `0-2-3-5-7-8-10` (W-H-W-W-H-W-W)

**Notes in A Aeolian:** A - B - C - D - E - F - G

**Character:**
- Dark, melancholic. introspective
- Most common minor scale
- Techno, dub, ambient

**Chord Quality:** Minor (vi)

**The "Aeolian" Sound:**
- Minor 3rd + minor 6th + minor 7th
- "Sad" or "dark" sound
- Most natural minor

**Best For:** Techno. dub, ambient, classical

**Famous Songs:**
- "All Along the Watchtower" - Jimi Hendrix
- "Losing My Religion" - R.E.M.
- "Smells Like Teen Spirit" - Nirvana
- Most minor key songs

**MCP Usage:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="minor", root=57)
```

---

### 7. Locrian Mode

**Intervals:** `0-1-3-5-6-8-10` (H-W-W-H-W-W-W)

**Notes in B Locrian:** B - C - D - E - F - G - A

**Character:**
- Unstable, dissonant, tense
- Diminished tonic chord
- Avant-garde, metal. horror

**Chord Quality:** Diminished (vii°)

**The "Locrian" Sound:**
- Diminished tonic (Bdim) = unstable
- No perfect 5th (tritone instead)
- Needs resolution

**Best For:** Avant-garde, metal. horror scores

**Famous Usage:**
- Black metal
- Avant-garde jazz
- Horror film scores
- Rare in popular music

**Why It's Rare:**
- Diminished tonic doesn't resolve
- No perfect 5th (tritone instead)
- Hard to establish tonal center

**MCP Usage:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="locrian", root=59)
```

---

## Mode Comparison Chart

| Mode | Intervals | Bright/Dark | Stability | Best Chord |
|------|-----------|-------------|-----------|------------|
| **Ionian** | 0-2-4-5-7-9-11 | Bright | Stable | I (Major) |
| **Dorian** | 0-2-3-5-7-9-10 | Neutral | Stable | ii (Minor) |
| **Phrygian** | 0-1-3-5-7-8-10 | Dark | Stable | iii (Minor) |
| **Lydian** | 0-2-4-6-7-9-11 | Bright | Unstable | IV (Major) |
| **Mixolydian** | 0-2-4-5-7-9-10 | Bright | Unstable | V (Dominant) |
| **Aeolian** | 0-2-3-5-7-8-10 | Dark | Stable | vi (Minor) |
| **Locrian** | 0-1-3-5-6-8-10 | Dark | Unstable | vii° (Diminished) |

---

## Modal Interchange

### What Is Modal Interchange?

**Modal interchange** (also called modal mixture) is borrowing chords from parallel scales or modes.

**Types:**
1. **Parallel Modes** - Using chords from the same mode starting on different roots
2. **Borrowed Chords** - Using chords from a different mode entirely

### Common Modal Interchanges

#### 1. Major → Mixolydian (Flat 7)

```
C Major: C - Dm - Em - F - G - Am - Bdim
Mixolydian: C - D - Em - F - G - Am - Bb (flat 7 instead of B)

Example: C - F - G7 - C
The G7 is borrowed from C Mixolydian
```

#### 2. Minor → Harmonic Minor (Major V)

```
A Minor: Am - Bdim - C - Dm - Em - F - G
Harmonic Minor: Am - Bdim - C - Dm - E - F - G# (major V)

Example: Am - Dm - E7 - Am
The E7 is borrowed from A Harmonic Minor
```

#### 3. Major → Lydian (Sharp 4)

```
C Major: C - Dm - Em - F - G - Am - Bdim
Lydian: C - D - Em - F# - G - Am - Bdim (F# instead of F)

Example: C - Dm - F#maj7 - C
The F#maj7 is borrowed from C Lydian
```

#### 4. Minor → Dorian (Major 6)

```
A Minor: Am - Bdim - C - Dm - Em - F - G
Dorian: Am - Bdim - C - Dm - Em - F# - G (F# instead of F)

Example: Am - Em - F#m7 - Em
This F#m7 is borrowed from A Dorian
```

---

## Modal Progressions

### Dorian Vamp

```
Dm7 - G7 (repeat)

Works over: D Dorian or G Mixolydian
```

**Analysis:**
- Static harmony (no dominant function)
- Modal ambiguity
- "So What" style

### Lydian Vamp

```
Fmaj7#11 - G7 (repeat)

Works over: F Lydian
```

**Analysis:**
- Sharp 4th creates tension
- Never resolves
- Dreamy quality

### Mixolydian Vamp

```
G7 - F (repeat)

Works over: G Mixolydian
```

**Analysis:**
- Flat 7th creates dominant quality
- Bluesy feel

---

## Mode Selection Guide by Genre

| Genre | Primary Modes | Secondary Modes |
|-------|--------------|-----------------|
| **House** | Dorian. Aeolian | Mixolydian. Ionian |
| **Techno** | Aeolian. Phrygian | Dorian. Locrian |
| **Dub Techno** | Aeolian. Dorian | Phrygian |
| **Trance** | Ionian. Lydian | Aeolian. Dorian |
| **Ambient** | Lydian. Aeolian | Dorian. Phrygian |
| **Jazz** | Dorian. Mixolydian | Ionian. Lydian |
| **Blues** | Mixolydian. Aeolian | Dorian |
| **Metal** | Phrygian. Aeolian | Locrian. Dorian |
| **Funk** | Dorian. Mixolydian | Ionian |
| **Film Scores** | Lydian. Dorian | Mixolydian. Aeolian |

---

## MCP Integration

### Create Mode Reference Clip

```python
# Dorian mode in D
create_scale_reference_clip(
    track_index=0,
    clip_index=0,
    scale="dorian",
    root=62,
    octaves=2
)
```

### Snap Notes to Mode

```python
# Force notes into G Mixolydian
snap_notes_to_scale(
    track_index=0,
    clip_index=0,
    scale="mixolydian",
    root=67
)
```

### Fire Scene with Mode

```python
# Fire scene and transpose to Lydian mode
fire_scene_with_transpose(scene_index=0, semitones=5)  # To F Lydian from C
```

### Detect Mode from Clip

```python
# Analyze what mode a clip is in
result = detect_clip_key(track_index=0, clip_index=0)
# Returns: {"key": "D Dorian", "camelot": "7A", "confidence": 0.85}
```

---

## Practice Exercises

### Exercise 1: Mode Identification

Identify the mode from these intervals:

1. `0-2-3-5-7-9-10`
2. `0-1-3-5-7-8-10`
3. `0-2-4-6-7-9-11`

<details>
<summary>Answer</summary>
1. Dorian (minor 3rd + major 6th)
2. Phrygian (minor 2nd + minor 3rd)
3. Lydian (major 3rd + augmented 4th)
</details>

### Exercise 2: Mode Matching

Match the song to its mode:

1. "So What" - Miles Davis
2. "Sweet Home Alabama" - Lynyrd Skynyrd
3. "Dreams" - Fleetwood Mac

<details>
<summary>Answer</summary>
1. D Dorian
2. G Mixolydian
3. F Lydian
</details>

### Exercise 3: Modal Interchange

Write a progression using modal interchange:

```
C Major: C - F - G7 - C
```

Add a borrowed chord from C Mixolydian.

<details>
<summary>Suggested Answer</summary>
C - F - G7 - Bb - C

The Bb is borrowed from C Mixolydian (flat 7).
</details>

---

## Further Reading

- **scales.md** - Scale theory and intervals
- **chords.md** - Chord construction
- **progressions.md** - Modal progressions
- **voice_leading.md** - Smooth modal transitions
- **exotic_scales.py** - Melodic/Harmonic minor modes

---

*Last updated: 2026-03-03*
