# Scales Reference Guide

> Comprehensive reference for scales used in electronic music production

---

## Quick Reference Table

| Scale | Intervals (Semitones) | Notes in C | Character | Best For |
|-------|----------------------|------------|-----------|----------|
| **Major** | 0-2-4-5-7-9-11 | C D E F G A B | Bright, happy | Pop, trance, house |
| **Natural Minor** | 0-2-3-5-7-8-10 | C D Eb F G Ab Bb | Dark, melancholic | Techno, dub, ambient |
| **Harmonic Minor** | 0-2-3-5-7-8-11 | C D Eb F G Ab B | Exotic, dramatic | Classical, metal, EDM |
| **Melodic Minor** | 0-2-3-5-7-9-11 | C D Eb F G A B | Sophisticated, jazzy | Jazz, fusion, neo-soul |
| **Dorian** | 0-2-3-5-7-9-10 | C D Eb F G A Bb | Soulful, minor with lift | Funk, house, jazz |
| **Phrygian** | 0-1-3-5-7-8-10 | C Db Eb F G Ab Bb | Spanish, dark | Flamenco, metal, techno |
| **Lydian** | 0-2-4-6-7-9-11 | C D E F# G A B | Dreamy, floating | Film scores, ambient |
| **Mixolydian** | 0-2-4-5-7-9-10 | C D E F G A Bb | Bluesy, rock | Blues, rock, funk |
| **Locrian** | 0-1-3-5-6-8-10 | C Db Eb F Gb Ab Bb | Unstable, dissonant | Avant-garde, metal |
| **Pentatonic Major** | 0-2-4-7-9 | C D E G A | Universal, open | Pop, folk, blues |
| **Pentatonic Minor** | 0-3-5-7-10 | C Eb F G Bb | Bluesy, rock | Blues, rock, metal |
| **Blues** | 0-3-5-6-7-10 | C Eb F Gb G Bb | Soulful, expressive | Blues, jazz, rock |
| **Whole Tone** | 0-2-4-6-8-10 | C D E F# G# A# | Dreamy, ambiguous | Impressionist, film |
| **Diminished** | 0-2-3-5-6-8-9-11 | C D Eb F Gb Ab A B | Tense, cinematic | Jazz, classical, horror |
| **Chromatic** | 0-1-2-3-4-5-6-7-8-9-10-11 | All 12 notes | Atonal, free | Atonal, experimental |

---

## Diatonic Scales (7 Notes)

### Major Scale (Ionian)

**Intervals:** `0-2-4-5-7-9-11` (W-W-H-W-W-W-H)

**Notes in C Major:** C - D - E - F - G - A - B

**Character:**
- Bright, happy, uplifting
- Most common scale in Western music
- Foundation for pop, rock, classical

**Chord Quality per Degree:**
```
I   - Major (C)
ii  - Minor (Dm)
iii - Minor (Em)
IV  - Major (F)
V   - Major (G)
vi  - Minor (Am) - Relative minor
vii° - Diminished (Bdim)
```

**Common Progressions:**
- I-V-vi-IV (Pop progression)
- I-IV-V (Rock progression)
- ii-V-I (Jazz cadence)

**MCP Command:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="major", root=60)
snap_notes_to_scale(track_index=0, clip_index=0, scale="major", root=60)
```

---

### Natural Minor Scale (Aeolian)

**Intervals:** `0-2-3-5-7-8-10` (W-H-W-W-H-W-W)

**Notes in A Minor:** A - B - C - D - E - F - G

**Character:**
- Dark, melancholic, introspective
- Most common minor scale in popular music
- Works well with techno, dub, ambient

**Chord Quality per Degree:**
```
i   - Minor (Am)
ii° - Diminished (Bdim)
III - Major (C)
iv  - Minor (Dm)
v   - Minor (Em)
VI  - Major (F)
VII - Major (G)
```

**Common Progressions:**
- i-VII-VI-VII (Blues minor)
- i-VI-III-VII (Emotional)
- i-iv-VII-III (Dramatic)

**MCP Command:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="minor", root=60)
```

---

### Harmonic Minor

**Intervals:** `0-2-3-5-7-8-11` (W-H-W-W-H-3H-H)

**Notes in A Harmonic Minor:** A - B - C - D - E - F - G#

**Character:**
- Exotic, dramatic, "snake charmer" sound
- Raised 7th creates leading tone
- Classical, metal, flamenco, EDM

**Unique Feature:** The augmented 2nd interval (F to G#) creates distinctive exotic sound

**Chord Quality per Degree:**
```
i   - Minor (Am)
ii° - Diminished (Bdim)
III+ - Augmented (C+)
iv  - Minor (Dm)
V   - Major (E) - Dominant quality!
VI  - Major (F)
vii°7 - Diminished 7th (G#dim7)
```

**Common Progressions:**
- i-V (Minor with dominant V)
- i-iv-V (Andalusian cadence)
- i-VII-VI-VII with V7 instead of VII

**MCP Usage:**
```python
# Not in default SCALE_INTERVALS - use exotic_scales.py
from music_theory.exotic_scales import HARMONIC_MINOR
```

---

### Melodic Minor (Jazz Minor)

**Intervals:** `0-2-3-5-7-9-11` (W-H-W-W-W-W-H)

**Notes in A Melodic Minor:** A - B - C - D - E - F# - G#

**Character:**
- Sophisticated, jazzy, smooth
- Ascending form of classical melodic minor
- Jazz, fusion, neo-soul

**Unique Feature:** Combines minor 3rd with major 6th and 7th

**Chord Quality per Degree:**
```
i   - Minor/major7 (Am(maj7))
ii  - Minor 7 (Bm7)
III+ - Augmented (C+)
IV  - Dominant 7 (D7)
V   - Dominant 7 (E7)
vi° - Half-diminished (F#m7b5)
vii° - Half-diminished (G#m7b5)
```

**Modes of Melodic Minor (Advanced):**
1. Melodic Minor (i)
2. Dorian b2 (ii) - Phrygian with major 6th
3. Lydian Augmented (III+) - Lydian with #5
4. Lydian Dominant (IV) - Lydian with b7
5. Mixolydian b6 (V) - Mixolydian with b6
6. Locrian #2 (vi°) - Locrian with natural 2
7. Super Locrian (vii°) - Altered scale

**MCP Usage:**
```python
from music_theory.exotic_scales import MELODIC_MINOR
```

---

## Modes of Major Scale

### Dorian Mode

**Intervals:** `0-2-3-5-7-9-10` (W-H-W-W-W-H-W)

**Notes in D Dorian:** D - E - F - G - A - B - C

**Relationship:** 2nd mode of C Major (D to D using C Major notes)

**Character:**
- Soulful, minor with brightness
- Minor 3rd + Major 6th
- Funk, house, jazz, fusion

**Signature Sound:** The major 6th (B in D Dorian) differentiates from natural minor

**Common Progressions:**
- i-IV (Dm7 - G7)
- i-ii-IV (Dm7 - Em7 - G7)
- i7-IV7 (So What voicing)

**Notable Tracks:**
- "So What" - Miles Davis
- "Oye Como Va" - Tito Puente / Santana
- "Get Lucky" - Daft Punk (D Dorian)

**MCP Command:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="dorian", root=60)
```

---

### Phrygian Mode

**Intervals:** `0-1-3-5-7-8-10` (H-W-W-W-H-W-W)

**Notes in E Phrygian:** E - F - G - A - B - C - D

**Relationship:** 3rd mode of C Major (E to E using C Major notes)

**Character:**
- Spanish, exotic, dark
- Flat 2nd creates tension
- Flamenco, metal, techno, film scores

**Signature Sound:** The minor 2nd (F in E Phrygian) creates "Spanish" sound

**Phrygian Dominant (Spanish Gypsy):**
- 5th mode of harmonic minor
- Intervals: `0-1-4-5-7-8-10`
- Major 3rd + minor 2nd = Spanish sound

**Common Progressions:**
- i-bII (E - F)
- i-bII-i (Flamenco cadence)
- i-VII-i-bII (Metal cadence)

**Notable Usage:**
- Flamenco music
- Metal (whitechapel, death metal)
- Middle Eastern music

**MCP Command:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="phrygian", root=60)
```

---

### Lydian Mode

**Intervals:** `0-2-4-6-7-9-11` (W-W-W-H-W-W-H)

**Notes in F Lydian:** F - G - A - B - C - D - E

**Relationship:** 4th mode of C Major (F to F using C Major notes)

**Character:**
- Dreamy, floating, ethereal
- Sharp 4th creates "lifting" sensation
- Film scores, ambient, progressive rock

**Signature Sound:** The augmented 4th/tritone (B in F Lydian) - "The Simpson's sound"

**Why It Works:**
- No avoid notes (all notes sound good over the chord)
- Major with extra brightness
- Resolves to itself (no strong pull)

**Common Progressions:**
- I-II (Fmaj7 - G7)
- I-vii (Fmaj7 - Em7)
- Lydian vamp (sustained I chord)

**Notable Tracks:**
- "Flying in a Blue Dream" - Joe Satriani
- "Dreams" - Fleetwood Mac (F Lydian)
- Film scores (Hans Zimmer, John Williams)

**MCP Command:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="lydian", root=60)
```

---

### Mixolydian Mode

**Intervals:** `0-2-4-5-7-9-10` (W-W-H-W-W-H-W)

**Notes in G Mixolydian:** G - A - B - C - D - E - F

**Relationship:** 5th mode of C Major (G to G using C Major notes)

**Character:**
- Bluesy, rock-oriented
- Major with flat 7
- Blues, rock, funk, jam bands

**Signature Sound:** The minor 7th (F in G Mixolydian) - dominant quality

**Dominant Chord Scale:**
- Works over dominant 7th chords
- G Mixolydian = G7 scale
- Foundation for blues improvisation

**Common Progressions:**
- I-bVII (G - F)
- I-bVII-IV (G - F - C)
- I-IV-I-bVII (Rock cadence)

**Notable Tracks:**
- "Sweet Child O' Mine" - Guns N' Roses
- "Sweet Home Alabama" - Lynyrd Skynyrd
- "Hey Jude" - The Beatles

**MCP Command:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="mixolydian", root=60)
```

---

### Locrian Mode

**Intervals:** `0-1-3-5-6-8-10` (H-W-W-H-W-W-W)

**Notes in B Locrian:** B - C - D - E - F - G - A

**Relationship:** 7th mode of C Major (B to B using C Major notes)

**Character:**
- Unstable, dissonant, tense
- Diminished tonic chord
- Avant-garde, metal, horror scores

**Signature Sound:** Diminished tonic (Bdim) - unstable, needs resolution

**Why It's Rare:**
- Diminished tonic chord doesn't resolve
- No perfect 5th (tritone instead)
- Hard to establish tonal center

**Usage:**
- Over diminished chords
- Tension passages
- Horror/suspense music

**Notable Usage:**
- Black metal
- Avant-garde jazz
- Horror film scores

---

## Pentatonic Scales (5 Notes)

### Major Pentatonic

**Intervals:** `0-2-4-7-9`

**Notes in C Major Pentatonic:** C - D - E - G - A

**Character:**
- Universal, open, folk-like
- No half steps = no tension
- Pop, folk, country, blues

**Relationship to Major Scale:**
- Major scale without 4th and 7th
- Removes "avoid notes"
- Works over major chords

**Grid Layout (C Major Pentatonic):**
```
    C   D   E   G   A   C   D   E
  +---+---+---+---+---+---+---+---+
  | 1 |   | 2 |   | 3 |   | 4 |   |
  +---+---+---+---+---+---+---+---+
```

**MCP Command:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="pentatonic_major", root=60)
```

---

### Minor Pentatonic

**Intervals:** `0-3-5-7-10`

**Notes in A Minor Pentatonic:** A - C - D - E - G

**Character:**
- Bluesy, rock-oriented
- No half steps = versatile
- Blues, rock, metal, funk

**Relationship to Natural Minor:**
- Natural minor without 2nd and 6th
- Removes "tension" notes
- Works over minor and dominant chords

**Blues Box Pattern:**
```
    E|---|---| A |---| C |---|---| C |
    A|---|---| D |---| E |---|---| E |
    D|---|---| G |---| A |---|---| A |
    G|---|---| C |---| D |---|---| D |
```

**MCP Command:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="pentatonic_minor", root=60)
```

---

### Blues Scale

**Intervals:** `0-3-5-6-7-10`

**Notes in A Blues:** A - C - D - Eb - E - G

**Character:**
- Soulful, expressive, "blue"
- Added flat 5 (blue note)
- Blues, jazz, rock

**Signature Sound:** The flat 5 (Eb in A Blues) - "blue note"

**Relationship to Minor Pentatonic:**
- Minor pentatonic + flat 5
- "Blue note" adds expression
- Works over blues progressions

**Blue Notes:**
- Flat 3 (C in A Blues)
- Flat 5 (Eb in A Blues)
- Flat 7 (G in A Blues)

**MCP Command:**
```python
create_scale_reference_clip(track_index=0, clip_index=0, scale="blues", root=60)
```

---

## Symmetric Scales

### Whole Tone Scale

**Intervals:** `0-2-4-6-8-10`

**Notes in C Whole Tone:** C - D - E - F# - G# - A#

**Character:**
- Dreamy, ambiguous, floating
- All whole steps = no tonal center
- Impressionist, film scores

**Unique Properties:**
- Only 2 distinct whole tone scales (C and C#)
- All chords are augmented
- No resolution, no leading tone

**Usage:**
- Over augmented chords
- Dream sequences
- "Magical" effects

**Notable Usage:**
- Debussy, Ravel
- Film scores (dream sequences)
- "Voiles" - Debussy

---

### Diminished Scale (Octatonic)

**Intervals:** `0-2-3-5-6-8-9-11` (W-H-W-H-W-H-W-H)

**Notes in C Diminished:** C - D - Eb - F - Gb - Ab - A - B

**Character:**
- Tense, cinematic, sophisticated
- Alternating whole-half pattern
- Jazz, classical, horror

**Two Forms:**
1. **Whole-Half Diminished:** W-H-W-H-W-H-W-H (starts with whole step)
2. **Half-Whole Diminished:** H-W-H-W-H-W-H-W (starts with half step)

**Chord Applications:**
- Whole-Half: Over diminished chords
- Half-Whole: Over dominant 7b9 chords

**Usage:**
- Over diminished chords
- Over V7b9 chords
- Tension passages

---

### Chromatic Scale

**Intervals:** `0-1-2-3-4-5-6-7-8-9-10-11`

**Notes:** All 12 semitones

**Character:**
- Aonal, free, dissonant
- No tonal center
- Atonal, experimental

**Usage:**
- Free jazz
- Atonal composition
- Transitional passages

---

## Exotic Scales

### Double Harmonic Major (Byzantine)

**Intervals:** `0-1-4-5-7-8-11`

**Notes in C:** C - Db - E - F - G - Ab - B

**Character:**
- Middle Eastern, exotic
- Phrygian dominant + raised 7th
- Arabic music, metal

---

### Hungarian Minor

**Intervals:** `0-2-3-6-7-8-11`

**Notes in A:** A - B - C - D# - E - F - G#

**Character:**
- Gypsy, exotic, dramatic
- Harmonic minor + raised 4th
- Gypsy jazz, classical

---

### Neapolitan Minor

**Intervals:** `0-1-3-5-7-8-11`

**Notes in A:** A - Bb - C - D - E - F - G#

**Character:**
- Classical, dramatic
- Phrygian + raised 7th
- Classical, opera

---

### Enigmatic Scale

**Intervals:** `0-1-4-6-8-10-11`

**Notes in C:** C - Db - E - F# - G# - A# - B

**Character:**
- Mysterious, ethereal
- Created by Verdi
- Classical, avant-garde

---

## Scale Selection Guide by Genre

### Electronic Music

| Genre | Primary Scales | Secondary Scales |
|-------|---------------|------------------|
| **Dub Techno** | Natural Minor, Dorian | Pentatonic Minor, Blues |
| **Deep House** | Dorian, Mixolydian | Pentatonic Minor, Blues |
| **Techno** | Natural Minor, Phrygian | Chromatic, Whole Tone |
| **Trance** | Major, Lydian | Natural Minor, Dorian |
| **Ambient** | Lydian, Whole Tone | Pentatonic Major, Dorian |
| **Drum & Bass** | Natural Minor, Dorian | Pentatonic Minor, Blues |

### Popular Music

| Genre | Primary Scales | Secondary Scales |
|-------|---------------|------------------|
| **Pop** | Major, Natural Minor | Pentatonic Major |
| **Rock** | Major, Mixolydian | Pentatonic Minor, Blues |
| **Blues** | Blues, Pentatonic Minor | Mixolydian |
| **Jazz** | Melodic Minor, Dorian | All modes |
| **R&B/Soul** | Dorian, Natural Minor | Pentatonic Minor |
| **Hip-Hop** | Natural Minor, Dorian | Pentatonic Minor, Blues |

---

## MCP Integration Examples

### Create Scale Reference Clip

```python
# Create a C minor scale clip (for Fold function)
create_scale_reference_clip(
    track_index=0,
    clip_index=0,
    scale="minor",
    root=60,  # C4
    octaves=3
)
```

### Snap Notes to Scale

```python
# Force out-of-key notes into A minor
snap_notes_to_scale(
    track_index=0,
    clip_index=0,
    scale="minor",
    root=57  # A3
)
```

### Detect Key from Clip

```python
# Analyze what key a clip is in
detect_clip_key(track_index=0, clip_index=0)
# Returns: {"key": "A minor", "camelot": "8A", "confidence": 0.85}
```

### Transpose to Compatible Key

```python
# Get compatible keys for harmonic mixing
get_compatible_keys("8A")
# Returns: {"one_up": "9A", "one_down": "7A", "relative": "8B"}

# Transpose all playing clips
transpose_all_playing_clips(semitones=2)  # Up 2 semitones
```

---

## Practice Exercises

### Exercise 1: Mode Recognition

Listen to each mode and identify by character:
1. **Ionian** - "Happy Birthday" starting note
2. **Dorian** - "So What" main riff
3. **Phrygian** - "Spanish" sounding
4. **Lydian** - "Dreams" by Fleetwood Mac
5. **Mixolydian** - "Sweet Home Alabama"

### Exercise 2: Scale Over Chords

Match scales to chord progressions:
- **Cmaj7** → C Major, C Lydian
- **Dm7** → D Dorian, D Natural Minor
- **G7** → G Mixolydian, G Blues
- **Am7** → A Natural Minor, A Dorian, A Blues

### Exercise 3: Genre Identification

Identify scale by genre character:
- **Dub techno bass** → Natural Minor, Dorian
- **House chord stabs** → Dorian, Mixolydian
- **Techno acid line** → Chromatic, Blues
- **Trance lead** → Major, Lydian

---

## Further Reading

- **AGENTS.md** - MCP command reference for scale operations
- **progressions.md** - Chord progressions by scale
- **modes.md** - Deep dive into modal theory
- **genre_theory.md** - Genre-specific scale usage

---

*Last updated: 2026-03-03*
