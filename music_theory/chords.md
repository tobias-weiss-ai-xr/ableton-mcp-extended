# Chords Reference Guide

> Comprehensive reference for chord construction, voicings, and usage in electronic music

---

## Quick Reference Table

### Basic Chords (Triads)

| Chord Type | Intervals | Notes in C | Symbol | Character |
|------------|-----------|------------|--------|-----------|
| **Major** | 0-4-7 | C-E-G | C, Cmaj | Bright, stable |
| **Minor** | 0-3-7 | C-Eb-G | Cm, Cmin | Dark, melancholic |
| **Diminished** | 0-3-6 | C-Eb-Gb | Cdim, C° | Tense, unstable |
| **Augmented** | 0-4-8 | C-E-G# | Caug, C+ | Dreamy, suspended |
| **Sus2** | 0-2-7 | C-D-G | Csus2 | Open, airy |
| **Sus4** | 0-5-7 | C-F-G | Csus4 | Tense, medieval |
| **Power** | 0-7 | C-G | C5 | Heavy, rock |

### 7th Chords (4 Notes)

| Chord Type | Intervals | Notes in C | Symbol | Character |
|------------|-----------|------------|--------|-----------|
| **Major 7** | 0-4-7-11 | C-E-G-B | Cmaj7 | Bright, jazzy |
| **Minor 7** | 0-3-7-10 | C-Eb-G-Bb | Cm7, Cmin7 | Smooth, soulful |
| **Dominant 7** | 0-4-7-10 | C-E-G-Bb | C7 | Bluesy, tense |
| **Diminished 7** | 0-3-6-9 | C-Eb-Gb-A | Cdim7, C°7 | Dark, cinematic |
| **Half-Diminished** | 0-3-6-10 | C-Eb-Gb-Bb | Cm7b5, Cø | Jazz, tense |
| **Minor/Major 7** | 0-3-7-11 | C-Eb-G-B | Cm(maj7) | Exotic, dramatic |

### Extended Chords (5+ Notes)

| Chord Type | Intervals | Notes in C | Symbol | Usage |
|------------|-----------|------------|--------|-------|
| **Major 9** | 0-4-7-11-14 | C-E-G-B-D | Cmaj9 | Jazz, neo-soul |
| **Minor 9** | 0-3-7-10-14 | C-Eb-G-Bb-D | Cm9 | Smooth jazz |
| **Dominant 9** | 0-4-7-10-14 | C-E-G-Bb-D | C9 | Funk, blues |
| **Dominant 11** | 0-4-7-10-14-17 | C-E-G-Bb-D-F | C11 | Jazz-funk |
| **Dominant 13** | 0-4-7-10-14-17-21 | C-E-G-Bb-D-F-A | C13 | Jazz, R&B |
| **Minor 11** | 0-3-7-10-14-17 | C-Eb-G-Bb-D-F | Cm11 | Jazz, neo-soul |

### Altered Dominants

| Chord Type | Intervals | Notes in C | Symbol | Character |
|------------|-----------|------------|--------|-----------|
| **7b5** | 0-4-6-10 | C-E-Gb-Bb | C7b5 | Tense, exotic |
| **7#5** | 0-4-8-10 | C-E-G#-Bb | C7#5 | Bluesy, intense |
| **7b9** | 0-4-7-10-13 | C-E-G-Bb-Db | C7b9 | Spanish, tense |
| **7#9** | 0-4-7-10-15 | C-E-G-Bb-D# | C7#9 | Rock, "Hendrix" |
| **7#5b9** | 0-4-8-10-13 | C-E-G#-Bb-Db | C7#5b9 | Altered, exotic |
| **7#5#9** | 0-4-8-10-15 | C-E-G#-Bb-D# | C7#5#9 | Altered, intense |

---

## Chord Construction Theory

### The Harmonic Series

Chords are built from the **harmonic series** (overtones):

```
Fundamental: C
1st overtone: C (octave)
2nd overtone: G (perfect 5th)
3rd overtone: C (octave)
4th overtone: E (major 3rd)
5th overtone: G (perfect 5th)
6th overtone: Bb (minor 7th - "blue note")
7th overtone: B (major 7th)
...
```

This explains why:
- Power chords (C-G) sound "natural"
- Major triads sound "bright" (major 3rd from harmonics)
- Dominant 7ths sound "bluesy" (minor 7th from harmonics)

### Stacking Thirds

All chords are built by **stacking thirds**:

```
Root (C)
  + major 3rd = E  → C-E (major 3rd)
  + minor 3rd = Eb → C-Eb (minor 3rd)

Triads:
  C-E-G   = Major (major 3rd + minor 3rd)
  C-Eb-G  = Minor (minor 3rd + major 3rd)
  C-Eb-Gb = Diminished (minor 3rd + minor 3rd)
  C-E-G#  = Augmented (major 3rd + major 3rd)

7th Chords:
  C-E-G-B   = Major 7 (add major 3rd)
  C-Eb-G-Bb = Minor 7 (add minor 3rd)
  C-E-G-Bb  = Dominant 7 (add minor 3rd)
  C-Eb-Gb-A = Diminished 7 (all minor 3rds)
```

---

## Chord Families

### Major Family

**Character:** Bright, stable, resolved

**Chord Types:**
- Major triad (C)
- Major 7 (Cmaj7)
- Major 9 (Cmaj9)
- Major 6 (C6)
- Major 6/9 (C6/9)
- Add9 (Cadd9)

**Works Over:**
- Major scale
- Lydian mode
- Major pentatonic

**Common Voicings:**

```
Cmaj7 (Root position):   C-E-G-B
Cmaj7 (Drop 2):          G-C-E-B (7th dropped)
Cmaj7 (3-7-9):           E-B-D (rootless)
Cmaj9:                   C-E-G-B-D
```

**MCP Command:**
```python
create_chord_notes(track_index=0, clip_index=0, root=60, chord_type="major")
```

---

### Minor Family

**Character:** Dark, melancholic, introspective

**Chord Types:**
- Minor triad (Cm)
- Minor 7 (Cm7)
- Minor 9 (Cm9)
- Minor 11 (Cm11)
- Minor 6 (Cm6)
- Minor/Major 7 (Cm(maj7))

**Works Over:**
- Natural minor scale
- Dorian mode
- Minor pentatonic

**Common Voicings:**

```
Cm7 (Root position):     C-Eb-G-Bb
Cm7 (Drop 2):            G-C-Eb-Bb
Cm9:                     C-Eb-G-Bb-D
Cm11:                    C-Eb-G-Bb-D-F
```

**MCP Command:**
```python
create_chord_notes(track_index=0, clip_index=0, root=60, chord_type="minor")
```

---

### Dominant Family

**Character:** Tense, bluesy, needs resolution

**Chord Types:**
- Dominant 7 (C7)
- Dominant 9 (C9)
- Dominant 11 (C11)
- Dominant 13 (C13)
- Altered dominants (C7b9, C7#9, etc.)

**Works Over:**
- Mixolydian mode
- Blues scale
- Altered scale (for altered dominants)

**Common Voicings:**

```
C7 (Root position):      C-E-G-Bb
C7 (Drop 2):             G-C-E-Bb
C9:                      C-E-G-Bb-D
C13:                     C-E-G-Bb-D-F-A (often omit 11)
C7#9 (Hendrix):          C-E-G-Bb-D#
```

**MCP Command:**
```python
create_chord_notes(track_index=0, clip_index=0, root=60, chord_type="dom7")
```

---

### Diminished Family

**Character:** Tense, unstable, cinematic

**Chord Types:**
- Diminished triad (Cdim)
- Diminished 7 (Cdim7)
- Half-diminished (Cm7b5, Cø)

**Works Over:**
- Diminished scale
- Locrian mode
- Harmonic minor (for dim7)

**Symmetric Property:**

```
Cdim7 = C-Eb-Gb-A
       = Eb-Gb-A-C (Ebdim7)
       = Gb-A-C-Eb (Gbdim7)
       = A-C-Eb-Gb (Adim7)

All 4 notes are equivalent roots!
```

**Common Voicings:**

```
Cdim7:                   C-Eb-Gb-A
Cm7b5 (Half-dim):        C-Eb-Gb-Bb
```

**MCP Command:**
```python
create_chord_notes(track_index=0, clip_index=0, root=60, chord_type="dim7")
```

---

### Suspended Family

**Character:** Open, unresolved, ethereal

**Chord Types:**
- Sus2 (Csus2)
- Sus4 (Csus4)
- 7sus4 (C7sus4)
- 9sus4 (C9sus4)

**Works Over:**
- Major scale
- Mixolydian mode
- Lydian mode

**Resolution Tendency:**

```
Csus4 → C (F resolves to E)
Csus2 → C (D can stay or resolve)
```

**Common Voicings:**

```
Csus2:                   C-D-G
Csus4:                   C-F-G
C7sus4:                  C-F-G-Bb
```

**MCP Command:**
```python
create_chord_notes(track_index=0, clip_index=0, root=60, chord_type="sus2")
create_chord_notes(track_index=0, clip_index=0, root=60, chord_type="sus4")
```

---

## Chord Inversions

### What Are Inversions?

Inversions change the **bass note** of a chord:

```
C Major Triad: C-E-G

Root Position:  C in bass (C-E-G)
1st Inversion:  E in bass (E-G-C)
2nd Inversion:  G in bass (G-C-E)
```

### Notation

| Position | Bass Note | Notation | Example |
|----------|-----------|----------|---------|
| Root | Root | C | C-E-G |
| 1st Inv | 3rd | C/E | E-G-C |
| 2nd Inv | 5th | C/G | G-C-E |
| 3rd Inv (7th) | 7th | C7/Bb | Bb-C-E-G |

### Why Use Inversions?

1. **Smoother Voice Leading** - Less jumping between chords
2. **Bass Line Motion** - Create melodic bass lines
3. **Different Color** - Same chord, different feel
4. **Register Control** - Keep chords in playable range

### Voice Leading Example

```
Bad (root position only):
Cmaj7 → Fmaj7 → G7 → Cmaj7
C-E-G-B  F-A-C-E  G-B-D-F  C-E-G-B
(lots of jumping)

Good (using inversions):
Cmaj7 → Fmaj7/C → G7/D → Cmaj7
C-E-G-B  C-F-A-E  D-G-B-F  C-E-G-B
(smoother voice leading, chromatic bass)
```

---

## Chord Voicings

### Drop 2 Voicings

**Definition:** Drop the 2nd note from the top down an octave

```
Cmaj7 (Close):  C-E-G-B
Cmaj7 (Drop 2): G-C-E-B (G dropped from top)

Cm7 (Close):    C-Eb-G-Bb
Cm7 (Drop 2):   G-C-Eb-Bb
```

**Why Use Drop 2?**
- More spread out, fuller sound
- Easier to play on guitar
- Common in jazz piano

### Drop 3 Voicings

**Definition:** Drop the 3rd note from the top down an octave

```
Cmaj7 (Close):  C-E-G-B
Cmaj7 (Drop 3): E-C-G-B (E dropped from top)
```

### Open vs Close Voicing

**Close Voicing:** All notes within one octave
```
Cmaj7: C-E-G-B (all within octave)
```

**Open Voicing:** Notes spread across multiple octaves
```
Cmaj7: C-G-E-B (5th in bass, 3rd on top)
```

### Shell Voicings (3-Note)

**Definition:** Only play essential notes (3rd and 7th)

```
Cmaj7: E-B (3rd + 7th)
Cm7:   Eb-Bb (3rd + 7th)
C7:    E-Bb (3rd + 7th)
```

**Why Use Shell Voicings?**
- Leaves room for bass player
- Cleaner sound in ensemble
- Common in jazz comping

### So What Voicing (4th Chords)

**Definition:** Stack perfect 4ths

```
Dm11: D-G-C-F (all 4ths)
Em11: E-A-D-G (all 4ths)
```

**Why Use 4th Voicings?**
- Modern, open sound
- Ambiguous tonality
- Used in modal jazz (Miles Davis "So What")

---

## Extended Chords Deep Dive

### 9th Chords

**Construction:** 7th chord + major 2nd (9th)

```
Cmaj9: C-E-G-B-D   (Major 7 + 9)
Cm9:   C-Eb-G-Bb-D (Minor 7 + 9)
C9:    C-E-G-Bb-D  (Dominant 7 + 9)
```

**When to Use:**
- Jazz, neo-soul, R&B
- Add sophistication to basic 7th chords
- Works well as tonic or subdominant

**MCP Usage:**
```python
from music_theory.extensions import create_extended_chord
create_extended_chord(root=60, chord_type="min9")
```

### 11th Chords

**Construction:** 9th chord + perfect 4th (11th)

```
Cm11: C-Eb-G-Bb-D-F
C11:  C-E-G-Bb-D-F (often omit 3rd to avoid clash)
```

**The 11th Problem:**
- Major 3rd (E) clashes with 11th (F)
- Solution: Omit 3rd or raise 11th (F#)

**Common Usage:**
- Minor 11: Very common in jazz
- Dominant 11: Omit 3rd, becomes "sus" chord

### 13th Chords

**Construction:** 11th chord + major 6th (13th)

```
C13: C-E-G-Bb-D-F-A (7 notes - too many!)
```

**Practical Voicing (Omit Notes):**
```
C13: C-E-Bb-A (root, 3rd, 7th, 13th)
C13: Bb-D-A (7th, 9th, 13th - rootless)
```

**Why Use 13th Chords:**
- Jazz, R&B, fusion
- Rich, sophisticated sound
- Often played as rootless voicings

---

## Altered Dominants

### What Are Altered Chords?

Altered dominants modify the **5th, 9th, 11th, or 13th** of a dominant 7 chord:

```
C7:    C-E-G-Bb
C7b5:  C-E-Gb-Bb  (flat 5)
C7#5:  C-E-G#-Bb  (sharp 5)
C7b9:  C-E-G-Bb-Db (flat 9)
C7#9:  C-E-G-Bb-D# (sharp 9)
```

### Why Use Altered Dominants?

1. **Increased Tension** - More pull to tonic
2. **Chromatic Voice Leading** - Smooth bass lines
3. **Jazz Sound** - Essential for jazz harmony
4. **Color** - Different altered tones = different colors

### Altered Scale

The **altered scale** (Super Locrian) works over all altered dominants:

```
C Altered: C-Db-Eb-F-Gb-Ab-Bb
          = 7th mode of Db Melodic Minor
```

Contains all alterations:
- b5 (Gb), #5 (Ab)
- b9 (Db), #9 (Eb)

### Common Altered Voicings

```
C7#9 (Hendrix chord): C-E-G-Bb-D#
C7b9:                 C-E-G-Bb-Db
C7#5b9:               C-E-G#-Bb-Db
C7alt (all):          C-Db-Eb-F-Gb-Ab-Bb
```

---

## Chord Substitution

### Tritone Substitution

**Concept:** Replace dominant 7 with dominant 7 a tritone away

```
Original: Dm7 → G7 → Cmaj7
Tritone sub: Dm7 → Db7 → Cmaj7
```

**Why It Works:**
- G7 and Db7 share the same 3rd and 7th
- G7: G-B-D-F (3rd=B, 7th=F)
- Db7: Db-F-Ab-Cb (3rd=F, 7th=Cb=B)

### Secondary Dominants

**Concept:** Dominant of a non-tonic chord

```
In C major:
V/V = D7 (dominant of G)
V/vi = A7 (dominant of Am)
V/ii = E7 (dominant of Dm)
```

**Usage:**
```
Cmaj7 → A7 → Dm7 → G7 → Cmaj7
       (V/vi) (ii)  (V)
```

### iii-VI-ii-V Substitution

**Original:** I-vi-ii-V
**Substitute:** I-III7-VI7-II7-V7

```
Original: Cmaj7 → Am7 → Dm7 → G7
Sub:      Cmaj7 → E7  → A7  → D7 → G7
```

---

## Chord Progression Examples

### Pop/Rock

| Progression | Chords in C | Roman Numerals |
|-------------|-------------|----------------|
| Pop | C-G-Am-F | I-V-vi-IV |
| Rock | C-F-G | I-IV-V |
| Sad Pop | Am-F-C-G | vi-IV-I-V |
| Jazz Pop | Cmaj7-Am7-Dm7-G7 | I-vi-ii-V |

### Jazz

| Progression | Chords in C | Description |
|-------------|-------------|-------------|
| ii-V-I | Dm7-G7-Cmaj7 | Most common jazz cadence |
| iii-vi-ii-V | Em7-Am7-Dm7-G7 | "Rhythm changes" turnaround |
| I-vi-ii-V | Cmaj7-Am7-Dm7-G7 | "Rhythm changes" A section |
| Circle of 5ths | Cmaj7-F#m7b5-B7-Em7... | Descending 5ths |

### Blues

| Progression | Chords in C | Description |
|-------------|-------------|-------------|
| 12-Bar Blues | C-C-C-C-F-F-C-C-G-F-C-C | Basic blues |
| Jazz Blues | C7-F7-C7-C7-F7-F7-C7-Em7-A7-Dm7-G7-C7-A7 | Jazzier version |
| Minor Blues | Cm7-Cm7-Cm7-Cm7-Fm7-Fm7-Cm7-Cm7-G7-G7-Cm7-Cm7 | Minor key blues |

---

## MIDI Note Reference

### Middle C = 60 (C4)

| Note | MIDI | Frequency |
|------|------|-----------|
| C4 | 60 | 261.63 Hz |
| C#4 | 61 | 277.18 Hz |
| D4 | 62 | 293.66 Hz |
| D#4 | 63 | 311.13 Hz |
| E4 | 64 | 329.63 Hz |
| F4 | 65 | 349.23 Hz |
| F#4 | 66 | 369.99 Hz |
| G4 | 67 | 392.00 Hz |
| G#4 | 68 | 415.30 Hz |
| A4 | 69 | 440.00 Hz |
| A#4 | 70 | 466.16 Hz |
| B4 | 71 | 493.88 Hz |

### Common Chord MIDI Ranges

| Chord Type | Bass Note Range | Chord Notes Range |
|------------|-----------------|-------------------|
| Sub-bass | 24-36 (C1-C2) | - |
| Bass | 36-48 (C2-C3) | - |
| Low Chords | 48-60 (C3-C4) | 48-72 |
| Mid Chords | 60-72 (C4-C5) | 60-84 |
| High Chords | 72-84 (C5-C6) | 72-96 |

---

## MCP Integration Examples

### Create Basic Chords

```python
# Major triad (C major)
create_chord_notes(track_index=0, clip_index=0, root=60, chord_type="major")

# Minor 7 (A minor 7)
create_chord_notes(track_index=0, clip_index=0, root=57, chord_type="min7")

# Dominant 7 (G7)
create_chord_notes(track_index=0, clip_index=0, root=55, chord_type="dom7")
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
```

### Create Extended Chords (Requires extensions.py)

```python
from music_theory.extensions import create_extended_chord

# Minor 11 chord
notes = create_extended_chord(root=60, chord_type="min11")
add_notes_to_clip(track_index=0, clip_index=0, notes=notes)
```

### Create Altered Dominants (Requires extensions.py)

```python
from music_theory.extensions import create_altered_chord

# Hendrix chord (C7#9)
notes = create_altered_chord(root=60, alterations=["#9"])
add_notes_to_clip(track_index=0, clip_index=0, notes=notes)
```

### Generate Voicings

```python
from music_theory.voicing import generate_voicing

# Drop 2 voicing for Cmaj7
notes = generate_voicing(root_note=60, chord_quality="maj7", voicing_type="drop_2")
add_notes_to_clip(track_index=0, clip_index=0, notes=[
    {"pitch": n, "start_time": 0, "duration": 4, "velocity": 100}
    for n in notes
])
```

---

## Practice Exercises

### Exercise 1: Chord Construction

Build these chords from root C4 (MIDI 60):
1. Cmaj7 = 60 + ___ + ___ + ___
2. Cm7 = 60 + ___ + ___ + ___
3. C7 = 60 + ___ + ___ + ___
4. Cdim7 = 60 + ___ + ___ + ___

<details>
<summary>Answers</summary>
1. Cmaj7 = 60 + 64 + 67 + 71 (C-E-G-B)
2. Cm7 = 60 + 63 + 67 + 70 (C-Eb-G-Bb)
3. C7 = 60 + 64 + 67 + 70 (C-E-G-Bb)
4. Cdim7 = 60 + 63 + 66 + 69 (C-Eb-Gb-A)
</details>

### Exercise 2: Chord Quality Identification

Identify these chords by intervals:
1. 0-4-7 = ?
2. 0-3-7-10 = ?
3. 0-4-7-10-14 = ?
4. 0-3-6-9 = ?

<details>
<summary>Answers</summary>
1. Major triad
2. Minor 7
3. Dominant 9
4. Diminished 7
</details>

### Exercise 3: Inversion Practice

Write these chords in 1st inversion:
1. Cmaj7 (C-E-G-B) → ?
2. Am7 (A-C-E-G) → ?
3. G7 (G-B-D-F) → ?

<details>
<summary>Answers</summary>
1. Cmaj7/E = E-G-B-C
2. Am7/C = C-E-G-A
3. G7/B = B-D-F-G
</details>

---

## Further Reading

- **scales.md** - Scales that work with each chord
- **progressions.md** - Chord progressions by genre
- **voice_leading.md** - Smooth voice leading techniques
- **extensions.py** - Extended chord construction code
- **voicing.py** - Voicing generation code

---

*Last updated: 2026-03-03*
