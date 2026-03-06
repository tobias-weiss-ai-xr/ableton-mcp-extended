# Chord Progressions Reference

> Common progressions by genre with Roman numerals, MIDI examples, and MCP integration

---

## Roman Numeral System

### Major Key

| Roman | Chord | In C Major | Quality |
|-------|-------|------------|---------|
| **I** | Tonic | C | Major |
| **ii** | Supertonic | Dm | Minor |
| **iii** | Mediant | Em | Minor |
| **IV** | Subdominant | F | Major |
| **V** | Dominant | G | Major |
| **vi** | Submediant | Am | Minor |
| **vii°** | Leading tone | Bdim | Diminished |

### Minor Key (Natural Minor)

| Roman | Chord | In A Minor | Quality |
|-------|-------|------------|---------|
| **i** | Tonic | Am | Minor |
| **ii°** | Supertonic | Bdim | Diminished |
| **III** | Mediant | C | Major |
| **iv** | Subdominant | Dm | Minor |
| **v** | Dominant | Em | Minor |
| **VI** | Submediant | F | Major |
| **VII** | Subtonic | G | Major |

### Minor Key (Harmonic Minor)

| Roman | Chord | In A Minor | Quality |
|-------|-------|------------|---------|
| **i** | Tonic | Am | Minor |
| **ii°** | Supertonic | Bdim | Diminished |
| **III+** | Mediant | C+ | Augmented |
| **iv** | Subdominant | Dm | Minor |
| **V** | Dominant | E | Major |
| **VI** | Submediant | F | Major |
| **vii°7** | Leading tone | G#dim7 | Diminished 7 |

---

## Pop Progressions

### The "Four Chords" (I-V-vi-IV)

**Most famous progression in pop music**

| Key | Chords | Example Songs |
|-----|--------|---------------|
| C Major | C - G - Am - F | "Don't Stop Believing", "Let It Be" |
| G Major | G - D - Em - C | "I'm Yours", "Pompeii" |
| D Major | D - A - Bm - G | "With or Without You" |
| A Major | A - E - F#m - D | "Someone Like You" |

**Why It Works:**
- Strong root movement (I → V)
- Relative minor adds emotion (vi)
- Subdominant creates lift (IV)
- Endless loop potential

**MCP Command:**
```python
create_chord_progression(
    track_index=0, clip_index=0,
    key="C", progression=["I", "V", "vi", "IV"],
    duration_per_chord=4
)
```

### Pop Variations

| Progression | Roman | Character | Example |
|-------------|-------|-----------|---------|
| Sad Pop | vi-IV-I-V | Melancholic | "Someone Like You" |
| Uplifting | I-IV-V | Bright | "Twist and Shout" |
| Emotional | I-V-vi-IV | Classic | "Let It Be" |
| Modern Pop | I-vi-IV-V | Contemporary | "Call Me Maybe" |
| Dark Pop | i-VI-III-VII | Minor | "Bad Guy" (Billie Eilish) |

---

## Rock Progressions

### Classic Rock (I-IV-V)

**The foundation of rock music**

| Key | Chords | Usage |
|-----|--------|-------|
| E Major | E - A - B | "La Bamba", "Twist and Shout" |
| G Major | G - C - D | "Sweet Home Alabama" |
| D Major | D - G - A | "Wild Thing" |

**Blues Variation:**
```
I - I - I - I
IV - IV - I - I
V - IV - I - V (turnaround)
```

### Rock Variations

| Progression | Roman | Genre | Example |
|-------------|-------|-------|---------|
| Classic | I-IV-V | Rock & Roll | "Johnny B. Goode" |
| Hard Rock | i-bVI-bIII-bVII | Metal | "Paranoid" |
| Punk | I-V-vi-IV | Pop-punk | "Basket Case" |
| Grunge | i-VII-VI-VII | Alternative | "Zombie" |

---

## Jazz Progressions

### ii-V-I (The Jazz Cadence)

**Most important progression in jazz**

| Key | Chords | Quality |
|-----|--------|---------|
| C Major | Dm7 - G7 - Cmaj7 | Major |
| F Major | Gm7 - C7 - Fmaj7 | Major |
| Bb Major | Cm7 - F7 - Bbmaj7 | Major |

**Why It Works:**
- ii shares 2 notes with IV (subdominant function)
- V creates tension (dominant function)
- I resolves (tonic function)

**Extended Version:**
```
ii9 - V13 - Imaj9
(Dm9 - G13 - Cmaj9)
```

**MCP Command:**
```python
create_chord_progression(
    track_index=0, clip_index=0,
    key="C", progression=["ii", "V", "I"],
    duration_per_chord=2
)
```

### Rhythm Changes (I-vi-ii-V)

**From Gershwin's "I Got Rhythm"**

| Key | Chords | A Section |
|-----|--------|-----------|
| Bb Major | Bb - Gm - Cm - F | Main |
| Bb Major | Bb - G7 - Cm - F7 | With dominants |

**Full AABA Structure:**
```
A: I-vi-ii-V (x2)
A: I-vi-ii-V (x2)
B: iii-VI-ii-V (bridge)
A: I-vi-ii-V (x2)
```

### Jazz Variations

| Progression | Roman | Name | Usage |
|-------------|-------|------|-------|
| Turnaround | I-vi-ii-V | Rhythm changes | Jazz standards |
| Bird Blues | I-VI-ii-V | Bebop | Charlie Parker |
| Coltrane | I-iii-vi-ii | Giant Steps | Advanced |
| Minor ii-V-i | ii°-V-i | Minor key | "Autumn Leaves" |

---

## Blues Progressions

### 12-Bar Blues

**Basic Form:**
```
| I  | I  | I  | I  | (bars 1-4)
| IV | IV | I  | I  | (bars 5-8)
| V  | IV | I  | V  | (bars 9-12)
```

**In A (classic blues key):**
```
| A7 | A7 | A7 | A7 |
| D7 | D7 | A7 | A7 |
| E7 | D7 | A7 | E7 |
```

### Jazz Blues

**More sophisticated:**
```
| I7   | IV7  | I7     | I7    |
| IV7  | iv7  | I7     | vi°7  |
| ii7  | V7   | I7-VI7 | ii7-V7|
```

**In F:**
```
| F7  | Bb7 | F7     | F7    |
| Bb7 | Bbm7| F7     | D7    |
| Gm7 | C7  | F7-D7  | Gm7-C7|
```

### Minor Blues

```
| im7 | im7 | im7 | im7 |
| ivm7| ivm7| im7 | im7 |
| V7  | ivm7| im7 | V7  |
```

**In C Minor:**
```
| Cm7 | Cm7 | Cm7 | Cm7 |
| Fm7 | Fm7 | Cm7 | Cm7 |
| G7  | Fm7 | Cm7 | G7  |
```

---

## Electronic Music Progressions

### House Music

#### Deep House (i-VII-VI-VII)

**In A Minor:**
```
Am7 - Gm7 - Fmaj7 - Gm7
```

**Character:** Soulful, smooth, groove-based

**MCP Command:**
```python
create_chord_progression(
    track_index=0, clip_index=0,
    key="Am", progression=["i", "VII", "VI", "VII"],
    duration_per_chord=4
)
```

#### Piano House (I-V-vi-IV)

**In C Major:**
```
Cmaj9 - G7 - Am9 - Fmaj9
```

**Character:** Uplifting, emotional, melodic

### Techno

#### Minimal Techno (Static Harmony)

**Single chord or 2-chord vamp:**
```
Am (repeat)
or
Am - Gm (oscillate)
```

**Character:** Hypnotic, repetitive, dark

#### Melodic Techno (i-bVI-bIII-bVII)

**In A Minor:**
```
Am - F - C - G
```

**Character:** Emotional, melodic, driving

### Dub Techno

#### Classic Dub (i-VII-VI-V)

**In A Minor:**
```
Am7 - Gm7 - Fmaj7 - E7
```

**Character:** Atmospheric, chord stabs, delay-heavy

**MCP Command:**
```python
create_chord_progression(
    track_index=0, clip_index=0,
    key="Am", progression=["i", "VII", "VI", "V"],
    duration_per_chord=8  # Longer for dub feel
)
```

### Trance

#### Uplifting Trance (i-VI-III-VII)

**In A Minor:**
```
Am - F - C - G
```

**Character:** Emotional, building, euphoric

#### Progressive Trance (i-bVI-bVII)

**In D Minor:**
```
Dm - Bb - C
```

**Character:** Progressive, building, hypnotic

---

## Reggae & Dub Progressions

### One Drop (i-VII-VI-VII)

**In A Minor:**
```
Am - G - F - G
```

**Character:** Roots reggae, heavy bass, offbeat rhythm

### Rockers (I-IV-I-V)

**In C Major:**
```
C - F - C - G
```

**Character:** Upbeat, danceable, positive

### Dub (i-VII-i-VII)

**In A Minor:**
```
Am - G - Am - G
```

**Character:** Stripped down, bass-heavy, space

**MCP Command:**
```python
create_chord_progression(
    track_index=0, clip_index=0,
    key="Am", progression=["i", "VII", "i", "VII"],
    duration_per_chord=2
)
```

### Reggae Variations

| Progression | Roman | Style | Example |
|-------------|-------|-------|---------|
| Roots | i-VII-VI-VII | Classic | "No Woman No Cry" |
| Rockers | I-IV-I-V | Upbeat | "Three Little Birds" |
| Dub | i-VII-i-VII | Minimal | King Tubby |
| Lovers Rock | I-vi-IV-V | Romantic | "Silly Games" |

---

## Hip-Hop Progressions

### Boom Bap (i-VII-VI-VII)

**In A Minor:**
```
Am7 - Gm7 - Fmaj7 - Gm7
```

**Character:** Classic 90s, soulful, sample-based

### Trap (i-bVI-bIII-bVII)

**In C Minor:**
```
Cm - Ab - Eb - Bb
```

**Character:** Dark, modern, 808-heavy

### Lo-Fi (i-VII-III-VII)

**In A Minor:**
```
Am7 - G7 - C7 - G7
```

**Character:** Chill, nostalgic, jazzy

---

## R&B / Neo-Soul Progressions

### Neo-Soul (ii-V-iii-VI)

**In C Major:**
```
Dm9 - G13 - Em9 - A13
```

**Character:** Sophisticated, smooth, jazzy

### R&B Ballad (I-iii-IV-iv)

**In C Major:**
```
Cmaj7 - Em7 - Fmaj7 - Fm7
```

**Character:** Emotional, romantic, smooth

### Gospel (I-IV-I-V/vi-vi)

**In C Major:**
```
C - F - C - G - Am
```

**Character:** Uplifting, powerful, soulful

---

## Modal Progressions

### Dorian Vamp (i-IV)

**In D Dorian:**
```
Dm7 - G7 (repeat)
```

**Character:** Modal jazz, "So What" style

**Why It Works:**
- No dominant function
- Sustained tension
- Modal ambiguity

### Lydian Vamp (I-II)

**In F Lydian:**
```
Fmaj7#11 - G7 (repeat)
```

**Character:** Dreamy, floating, sci-fi

### Mixolydian Rock (I-bVII)

**In G Mixolydian:**
```
G - F (repeat)
```

**Character:** Bluesy, rock, jam band

---

## Passing Chords & Substitutions

### Secondary Dominants

**Dominant of a non-tonic chord:**

| Secondary | In C Major | Function |
|-----------|------------|----------|
| V/V | D7 | Pushes to G |
| V/vi | A7 | Pushes to Am |
| V/ii | E7 | Pushes to Dm |
| V/IV | C7 | Pushes to F |

**Example:**
```
Cmaj7 → A7 → Dm7 → G7 → Cmaj7
       (V/vi) (ii)  (V)
```

### Tritone Substitution

**Replace V7 with dominant 7 a tritone away:**

```
Original: Dm7 → G7 → Cmaj7
Sub:      Dm7 → Db7 → Cmaj7
```

### Diminished Passing

**Use diminished to connect:**

```
Cmaj7 → C#dim7 → Dm7
       (passing)
```

---

## Progression Analysis

### Functional Harmony

Every chord has a function:

| Function | Role | Examples |
|----------|------|----------|
| **Tonic** | Home, stable | I, vi, iii |
| **Subdominant** | Moves away, prepares | IV, ii |
| **Dominant** | Creates tension, pulls to I | V, vii° |

**Typical Flow:**
```
Tonic → Subdominant → Dominant → Tonic
   I    →     IV      →    V    →   I
```

### Circle of Fifths Progressions

**Descending 5ths:**
```
C → F → Bm7b5 → E7 → Am → Dm → G7 → C
```

**Why It Works:**
- V7-I resolution each step
- Strong forward motion
- Jazz standard convention

---

## MCP Integration

### Create Progression

```python
# Basic pop progression
create_chord_progression(
    track_index=0,
    clip_index=0,
    key="C",
    progression=["I", "V", "vi", "IV"],
    duration_per_chord=4
)
```

### Minor Key Progression

```python
# Dub techno progression
create_chord_progression(
    track_index=0,
    clip_index=0,
    key="Am",
    progression=["i", "VII", "VI", "V"],
    duration_per_chord=8
)
```

### Jazz Progression

```python
# ii-V-I in F
create_chord_progression(
    track_index=0,
    clip_index=0,
    key="F",
    progression=["ii", "V", "I"],
    duration_per_chord=2
)
```

### Blues Progression

```python
# 12-bar blues in A
create_chord_progression(
    track_index=0,
    clip_index=0,
    key="A",
    progression=["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"],
    duration_per_chord=1
)
```

### Transpose Progression

```python
# Transpose progression for key change
batch_transpose_clips(
    clips=[{"track_index": 0, "clip_index": 0}],
    semitones=2  # Up 2 semitones
)
```

---

## Quick Reference Cards

### Pop/Rock Card

| Feel | Progression | Key |
|------|-------------|-----|
| Happy | I-IV-V | C-F-G |
| Sad | vi-IV-I-V | Am-F-C-G |
| Classic | I-V-vi-IV | C-G-Am-F |
| Rock | I-IV-I-V | C-F-C-G |

### Jazz Card

| Style | Progression | Key |
|-------|-------------|-----|
| Bebop | ii-V-I | Dm7-G7-Cmaj7 |
| Ballad | I-vi-ii-V | C-Am-Dm-G |
| Modal | i-IV | Dm7-G7 |
| Blues | I-IV-I-V | C7-F7-C7-G7 |

### Electronic Card

| Genre | Progression | Key |
|-------|-------------|-----|
| House | i-VII-VI-VII | Am-G-F-G |
| Techno | i-bVI-bIII-bVII | Am-F-C-G |
| Trance | i-VI-III-VII | Am-F-C-G |
| Dub | i-VII-i-VII | Am-G-Am-G |

---

## Further Reading

- **chords.md** - Chord construction and types
- **scales.md** - Scales for each progression
- **genre_theory.md** - Genre-specific progressions
- **voice_leading.md** - Smooth transitions

---

*Last updated: 2026-03-03*
