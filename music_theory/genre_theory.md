# Genre Theory Reference

> Deep dive into music theory for electronic genres: Dub Techno, House, Techno, Reggae, and more

---

## Dub Techno

### Character & Origins

**Origins:** Berlin, early 1990s (Basic Channel, Chain Reaction)

**Key Elements:**
- Heavy use of delay and reverb
- Minimal, evolving chord stabs
- Deep sub-bass
- Atmospheric pads
- Rhythmic repetition

### Scale Theory

**Primary Scales:**

| Scale | Usage | Character |
|-------|-------|-----------|
| Natural Minor | Most common | Dark, hypnotic |
| Dorian | For brightness | Soulful, minor with lift |
| Pentatonic Minor | Bass lines | Stripped down |

**Typical Keys:**
- A minor (8A)
- E minor (9A)
- D minor (7A)

### Chord Theory

**Chord Types:**

| Chord | Usage | Example |
|-------|-------|---------|
| Minor 7 | Main stabs | Am7 |
| Minor 9 | Extended stabs | Am9 |
| Major 7 | Occasional brightness | Cmaj7 |
| Sus2 | Atmospheric | Asus2 |

**Progression:**

```
i - VII - VI - V (Am - G - F - E)
or
i - VII - i - VII (Am - G - Am - G)
```

**Voicing Technique:**

```
Standard:      A-C-E-G
Spread:        A-E-C-G (5th in middle)
Dub style:     A-E-G-C (open, with extensions)
```

### Rhythm Theory

**Kick Patterns:**

```
Basic:         X---X---X---X---
Syncopated:    X-----X-X---X---
Offbeat:       --X---X---X---X-
```

**Hi-Hat:**

```
8th notes:     X---X---X---X---
16th notes:    X-X-X-X-X-X-X-X-
Offbeat:       ----X-------X---
```

**Characteristic:** Long delay tails on hi-hats create "wash" effect

### Sound Design Theory

**Chord Stabs:**
- Low-pass filter (800-2000 Hz)
- Long release on envelope
- Send to delay (1/4 or 1/8 note)
- Send to reverb (plate or hall)

**Bass:**
- Sine wave or filtered square
- Sub frequencies (30-60 Hz)
- Sustained notes
- Sidechain to kick

**Pads:**
- Slow attack (500ms+)
- Low-pass filter automation
- LFO on filter cutoff
- Long reverb tails

### MCP Implementation

```python
# Setup dub techno session
set_tempo(126)
create_midi_track(0)  # Kick
create_midi_track(1)  # Bass
create_midi_track(2)  # Chords
create_midi_track(3)  # Hats

# Create chord progression
create_chord_progression(
    track_index=2, clip_index=0,
    key="Am", progression=["i", "VII", "VI", "V"],
    duration_per_chord=8
)

# Create drum pattern
create_drum_pattern(
    track_index=0, clip_index=0,
    pattern_name="dub_techno",
    length=4
)
```

---

## House Music

### Character & Origins

**Origins:** Chicago, mid-1980s (Frankie Knuckles, Ron Hardy)

**Key Elements:**
- 4/4 kick drum
- Offbeat hi-hats
- Synth stabs
- Soulful vocals
- Disco samples

### Scale Theory

**Primary Scales:**

| Scale | Subgenre | Character |
|-------|----------|-----------|
| Dorian | Deep House | Soulful, jazzy |
| Natural Minor | Tech House | Dark, driving |
| Pentatonic Minor | Classic House | Bluesy, catchy |
| Mixolydian | Funky House | Bright, groovy |

### Chord Theory

**Deep House Chords:**

| Chord | Usage | Voicing |
|-------|-------|---------|
| Minor 9 | Main | R-b3-5-b7-9 |
| Minor 11 | Extended | R-b3-5-b7-9-11 |
| Dominant 9 | Transitions | R-3-5-b7-9 |
| Major 7 | Uplifting | R-3-5-7 |

**Progressions:**

```
Deep House:    i - VII - VI - VII (Am - G - F - G)
Soulful:       ii - V - iii - VI (Dm7 - G7 - Em7 - Am7)
Classic:       I - vi - IV - V (C - Am - F - G)
```

### Rhythm Theory

**Kick:**
```
4/4:           X---X---X---X---
```

**Hi-Hats:**
```
Closed:        X-X-X-X-X-X-X-X-
Open:          ----X-------X--- (on 2& and 4&)
```

**Clap/Snare:**
```
Backbeat:      ----X-------X--- (on 2 and 4)
```

**Swing:**
- Deep House: 55-60% swing
- Chicago House: Straight (50%)

### Bass Theory

**Types:**

| Type | Sound | Pattern |
|------|-------|---------|
| Sub Bass | Sine wave, sustained | Long notes |
| Acid | 303 squelch | 16th note patterns |
| Funky | Slap bass | Syncopated |
| Deep | Filtered square | Offbeat |

**Pattern:**

```
Basic:         X-------X-------
Offbeat:       --X-----X---X---
Walking:       X-X-X-X-X-X-X-X-
```

### MCP Implementation

```python
# Setup house session
set_tempo(124)

# Create chord progression
create_chord_progression(
    track_index=0, clip_index=0,
    key="Am", progression=["i", "VII", "VI", "VII"],
    duration_per_chord=4
)

# Create drum pattern
create_drum_pattern(
    track_index=1, clip_index=0,
    pattern_name="house_basic",
    length=4
)

# Add bass
create_clip(track_index=2, clip_index=0, length=4)
bass_notes = [
    {"pitch": 36, "start_time": 0, "duration": 0.5, "velocity": 100},
    {"pitch": 36, "start_time": 1, "duration": 0.5, "velocity": 100},
    {"pitch": 36, "start_time": 2, "duration": 0.5, "velocity": 100},
    {"pitch": 36, "start_time": 3, "duration": 0.5, "velocity": 100},
]
add_notes_to_clip(track_index=2, clip_index=0, notes=bass_notes)
```

---

## Techno

### Character & Origins

**Origins:** Detroit, mid-1980s (Juan Atkins, Derrick May, Kevin Saunderson)

**Key Elements:**
- Driving, repetitive beats
- Synthetic sounds
- Minimal arrangements
- Industrial textures
- Hypnotic patterns

### Scale Theory

**Primary Scales:**

| Scale | Subgenre | Character |
|-------|----------|-----------|
| Natural Minor | All techno | Dark, hypnotic |
| Phrygian | Industrial | Spanish, tense |
| Chromatic | Experimental | Atonal, free |
| Whole Tone | Ambient techno | Dreamy |

### Chord Theory

**Minimal Chords:**

| Chord | Usage | Notes |
|-------|-------|-------|
| Power chord | Riff basis | Root + 5th |
| Minor triad | Dark stabs | R-b3-5 |
| Diminished | Tension | R-b3-b5 |
| Augmented | Unsettling | R-3-#5 |

**Progressions:**

```
Minimal:       i - i - i - i (static harmony)
Oscillating:   i - bVI - i - bVI (Am - F - Am - F)
Industrial:    i - bII - i - bII (Am - Bb - Am - Bb)
```

### Rhythm Theory

**Kick:**
```
Driving:       X---X---X---X---
Syncopated:    X-X-X-X-X-X-X-X-
Broken:        X-----X-X---X---
```

**Hi-Hats:**
```
Offbeat:       --X---X---X---X-
16ths:         X-X-X-X-X-X-X-X-
Tight:         --x---x---x---x (ghost velocity)
```

**Clap:**
```
Every bar:     ----X-----------
Every 2 bars:  ----X-------X---
```

### Sound Design

**Synth Leads:**
- Sawtooth wave
- Filter modulation
- LFO on pitch
- Distortion

**Bass:**
- Sine or triangle
- Sustained
- Sidechain
- Sub emphasis

**FX:**
- Noise sweeps
- Filter builds
- Reverb tails
- Delay feedback

### MCP Implementation

```python
# Setup techno session
set_tempo(132)

# Create minimal pattern
create_drum_pattern(
    track_index=0, clip_index=0,
    pattern_name="techno_4x4",
    length=4
)

# Create bass pattern
create_clip(track_index=1, clip_index=0, length=4)
bass = [{"pitch": 36, "start_time": i, "duration": 0.9, "velocity": 100} for i in range(4)]
add_notes_to_clip(track_index=1, clip_index=0, notes=bass)
```

---

## Reggae & Dub

### Character & Origins

**Origins:** Jamaica, late 1960s (Lee "Scratch" Perry, King Tubby)

**Key Elements:**
- Heavy bass
- Offbeat rhythms (skank)
- Delay and reverb
- Versioning/remixing
- Sound system culture

### Scale Theory

**Primary Scales:**

| Scale | Usage | Character |
|-------|-------|-----------|
| Natural Minor | Roots | Serious, conscious |
| Dorian | Modern reggae | Soulful |
| Pentatonic Minor | Bass lines | Funky |
| Mixolydian | Dancehall | Bright, energetic |

### Chord Theory

**Common Chords:**

| Chord | Usage | Example |
|-------|-------|---------|
| Minor | Most common | Am, Dm, Em |
| Dominant 7 | Transitions | G7, E7 |
| Major 7 | Uplifting | Cmaj7 |
| Sus4 | Tension | Asus4 |

**Progressions:**

```
One Drop:      i - VII - VI - VII (Am - G - F - G)
Rockers:       I - IV - I - V (C - F - C - G)
Dub:           i - VII - i - VII (Am - G - Am - G)
Lovers Rock:   I - vi - IV - V (C - Am - F - G)
```

### Rhythm Theory

**Drums:**

```
One Drop:      Kick on 1 and 3+, Snare on 3
Kick:          X---------X-----
Snare:         ----X-------X---
Hat:           X-X-X-X-X-X-X-X-

Steppers:      Kick on every beat
Kick:          X-X-X-X-X-X-X-X-
Snare:         ----X-------X---
Hat:           X-X-X-X-X-X-X-X-

Rockers:       Kick on 1, 2+, 3, 4+
Kick:          X---X-----X-X---
Snare:         ----X-------X---
Hat:           X-X-X-X-X-X-X-X-
```

**Skank (Guitar/Keys):**

```
Chord stabs on 2 and 4 (with anticipation on 1+ and 3+):
X-----X-X-----X-
1   2   3   4
```

### Bass Theory

**Characteristics:**
- Heavily emphasized
- Melodic, not just root notes
- Syncopated
- Often doubled with guitar

**Pattern:**

```
Roots:         X---------X----- (sparse)
Modern:        X-X-----X-X----- (syncopated)
Steppers:      X-X-X-X-X-X-X-X- (driving)
```

### Sound Design

**Dub Techniques:**
- Heavy reverb on drums/snare
- Delay on vocals/instruments
- Filter sweeps
- Drop-outs (removing elements)
- Versioning (reusing riddims)

**Mix Philosophy:**
- Bass is king
- Space is important
- FX as instruments
- Version over composition

### MCP Implementation

```python
# Setup dub session
set_tempo(72)  # Half-time feel

# Create one drop pattern
create_drum_pattern(
    track_index=0, clip_index=0,
    pattern_name="one_drop",
    length=4
)

# Create chord progression
create_chord_progression(
    track_index=1, clip_index=0,
    key="Am", progression=["i", "VII", "VI", "VII"],
    duration_per_chord=2
)

# Create bass line
create_clip(track_index=2, clip_index=0, length=4)
bass = [
    {"pitch": 36, "start_time": 0, "duration": 1, "velocity": 127},
    {"pitch": 36, "start_time": 1.5, "duration": 0.5, "velocity": 100},
    {"pitch": 36, "start_time": 2, "duration": 1, "velocity": 127},
    {"pitch": 36, "start_time": 3.5, "duration": 0.5, "velocity": 100},
]
add_notes_to_clip(track_index=2, clip_index=0, notes=bass)
```

---

## Trance

### Character & Origins

**Origins:** Germany/UK, early 1990s

**Key Elements:**
- Building energy
- Melodic leads
- Breakdowns
- Uplifting progressions
- Arpeggiated synths

### Scale Theory

**Primary Scales:**

| Scale | Subgenre | Character |
|-------|----------|-----------|
| Major | Uplifting | Euphoric |
| Natural Minor | Progressive | Emotional |
| Lydian | Epic | Dreamy |
| Dorian | Tech trance | Driving |

### Chord Theory

**Chords:**

| Chord | Usage | Example |
|-------|-------|---------|
| Major 9 | Uplifting | Cmaj9 |
| Minor 9 | Emotional | Am9 |
| Sus2 | Building | Asus2 |
| Add9 | Bright | Cadd9 |

**Progressions:**

```
Uplifting:     i - VI - III - VII (Am - F - C - G)
Progressive:   i - bVI - bVII (Am - F - G)
Epic:          I - V - vi - IV (C - G - Am - F)
```

### Rhythm Theory

**Kick:**
```
4/4:           X---X---X---X---
```

**Hi-Hats:**
```
Offbeat:       ----X-------X---
16ths:         X-X-X-X-X-X-X-X-
Open (build):  X-X-X-X-X-X-X-X- (increasing velocity)
```

**Snare Roll:**
```
Build:         --xx--xx--xxxx-- (velocity crescendo)
```

### MCP Implementation

```python
# Setup trance session
set_tempo(138)

# Create uplifting progression
create_chord_progression(
    track_index=0, clip_index=0,
    key="Am", progression=["i", "VI", "III", "VII"],
    duration_per_chord=8
)

# Create drum pattern
create_drum_pattern(
    track_index=1, clip_index=0,
    pattern_name="techno_4x4",
    length=4
)
```

---

## Drum & Bass

### Character & Origins

**Origins:** UK, early 1990s (breakbeat hardcore evolution)

**Key Elements:**
- Fast tempos (160-180 BPM)
- Complex breakbeats
- Heavy bass
- Syncopated rhythms
- Sub-bass emphasis

### Scale Theory

**Primary Scales:**

| Scale | Subgenre | Character |
|-------|----------|-----------|
| Natural Minor | Dark | Aggressive |
| Dorian | Liquid | Soulful |
| Pentatonic Minor | Jump up | Energetic |
| Harmonic Minor | Neuro | Tense |

### Chord Theory

**Progressions:**

```
Dark:          i - bVI - bIII - bVII (Am - F - C - G)
Liquid:        vi - IV - I - V (Am - F - C - G)
Neuro:         i - bII - i - bII (Am - Bb - Am - Bb)
```

### Rhythm Theory

**Breakbeat Pattern:**

```
Kick:          X-----X-X---X-X-
Snare:         ----X-------X---
Hat:           X-X-X-X-X-X-X-X-

Based on "Amen Break":
Kick:          X-----X-XX--X-X-
Snare:         ----X-----X---X-
```

**Amen Break (Full):**

```
Beat 1-2:      X-----X-XX--X-X-
               ----X-----X---X-
Beat 3-4:      X-----X-X---X-X-
               ----X-------X---
```

### MCP Implementation

```python
# Setup DnB session
set_tempo(174)

# Create amen-style pattern
create_clip(track_index=0, clip_index=0, length=4)

# Kick pattern
kick_notes = [
    {"pitch": 36, "start_time": 0, "duration": 0.25, "velocity": 127},
    {"pitch": 36, "start_time": 1.5, "duration": 0.25, "velocity": 100},
    {"pitch": 36, "start_time": 2, "duration": 0.25, "velocity": 127},
    {"pitch": 36, "start_time": 2.25, "duration": 0.25, "velocity": 90},
    {"pitch": 36, "start_time": 3, "duration": 0.25, "velocity": 127},
    {"pitch": 36, "start_time": 3.5, "duration": 0.25, "velocity": 100},
]
add_notes_to_clip(track_index=0, clip_index=0, notes=kick_notes)

# Snare pattern
snare_notes = [
    {"pitch": 38, "start_time": 1, "duration": 0.25, "velocity": 127},
    {"pitch": 38, "start_time": 2.5, "duration": 0.25, "velocity": 110},
    {"pitch": 38, "start_time": 3, "duration": 0.25, "velocity": 127},
]
add_notes_to_clip(track_index=0, clip_index=0, notes=snare_notes)
```

---

## Hip-Hop

### Character & Origins

**Origins:** Bronx, NYC, 1970s

**Key Elements:**
- Sampled breaks
- Heavy bass (808)
- Syncopated rhythms
- Minimal arrangements
- Strong groove

### Scale Theory

**Primary Scales:**

| Scale | Subgenre | Character |
|-------|----------|-----------|
| Natural Minor | Boom bap | Dark, gritty |
| Dorian | Neo-soul | Jazzy |
| Pentatonic Minor | Trap | Modern |
| Blues | Classic | Soulful |

### Chord Theory

**Progressions:**

```
Boom Bap:      i - VII - VI - VII (Am - G - F - G)
Trap:          i - bVI - bIII - bVII (Am - F - C - G)
Lo-Fi:         i - VII - III - VII (Am - G - C - G)
```

### Rhythm Theory

**Boom Bap:**

```
Kick:          X-------X---X---
Snare:         ----X-------X---
Hat:           X-X-X-X-X-X-X-X-
```

**Trap:**

```
Kick:          X---------X-X---
Snare:         ----X-------X---
Hat:           XXXXXXXXXXXXXXXX (rapid)
808:           X---------X-X--- (sustained)
```

### 808 Bass Theory

**Characteristics:**
- Sine wave
- Long sustain
- Pitch envelope (optional)
- Saturation for harmonics
- Sidechain to kick

**Pattern:**

```
Trap 808:      X---------X-X---
Pitch:         ↓--~~~~~--↓-↓--- (glides)
```

---

## Genre Quick Reference

| Genre | BPM | Scale | Key Pattern | Bass Style |
|-------|-----|-------|-------------|------------|
| **Dub Techno** | 110-130 | Minor | i-VII-VI-V | Sub, sustained |
| **House** | 115-130 | Dorian/Minor | i-VII-VI-VII | Offbeat, funky |
| **Techno** | 125-145 | Minor/Chromatic | i-i-i-i (static) | Driving, minimal |
| **Reggae** | 60-80 | Minor | i-VII-VI-VII | Heavy, melodic |
| **Trance** | 125-150 | Major/Minor | i-VI-III-VII | Offbeat, driving |
| **DnB** | 160-180 | Minor | Breakbeat | Sub, Reese |
| **Hip-Hop** | 80-100 | Minor | i-VII-VI-VII | 808, sub |

---

## Further Reading

- **scales.md** - Scale theory for each genre
- **chords.md** - Chord types used in genres
- **progressions.md** - Progression patterns
- **rhythm.md** - Drum patterns by genre

---

*Last updated: 2026-03-03*
