# Generative Music Workflow Guide

**Complete guide to MIDI generative tools in ableton-mcp-extended.**

---

## Quick Start (3 Steps)

Fastest path to a complete generative session:

```python
# Step 1: Create full session
create_generative_session(
    genre="dub_techno",
    key="Fm",
    num_tracks=4,
    clips_per_track=8,
    include_drums=True,
    include_bass=True,
    include_chords=True,
    include_melody=True,
    tempo=120
)

# Step 2: Manual setup (in Ableton)
# - Configure instrument presets on each track
# - Set up send routing
# - Adjust initial mix levels

# Step 3: Start playback
start_playback()
```

**Result:** 4 tracks, 32 clips, fully configured generative session ready for playback.

---

## Tool Overview

### 1. apply_midi_effect_preset

Apply preset configuration to loaded MIDI effects.

```
apply_midi_effect_preset(
    track_index=0,
    effect_name="arpeggiator",
    preset_name="techno_up",
    device_index=None  # Auto-detect if omitted
)
```

**Available Effects:**
- arpeggiator: techno_up, techno_down, trance, ambient, dub_echo
- chord: dub_minor, dub_major, dub_seven, dub_ninth, dub_minor_ninth
- scale: f_minor, c_minor, d_minor, chromatic, pentatonic
- velocity: dub_heavy, dub_soft, random_human, accent_beats
- pitch: octave_up, octave_down, fifth_up, fourth_up, dub_detune

**Use Case:** Quickly configure MIDI effects after loading them.

---

### 2. get_generative_chain_presets

Get available chain presets and their configurations.

```python
# Returns JSON with all preset info
get_generative_chain_presets()
```

**Output:**
```
{
  "dub_techno": {
    "description": "Classic dub techno generative chain",
    "effects": ["scale", "chord", "velocity"],
    "use_case": "Hypnotic dub techno with deep chords and humanized velocity"
  },
  "house": {
    "description": "Driving house music chain with arpeggiator",
    "effects": ["scale", "chord", "arpeggiator", "velocity"]
  }
}
```

**Use Case:** Explore chain configurations before applying them.

---

### 3. create_generative_chain

Load complete MIDI effect chain with genre-appropriate configuration.

```python
create_generative_chain(
    track_index=0,
    chain_type="dub_techno",
    key="Fm",
    include_arpeggiator=False
)
```

**Chain Types:**
- dub_techno: Scale(Fm) → Chord(dub_minor) → Velocity(random_human)
- house: Scale(C) → Chord(dub_major) → Arpeggiator(techno_up) → Velocity(dub_soft)
- techno: Scale(Em, phrygian) → Arpeggiator(techno_up) → Velocity(dub_heavy)
- ambient: Scale(F, lydian) → Chord(dub_seven) → Velocity(random_human)

**Use Case:** Set up entire MIDI effect chain in one command.

---

### 4. create_generative_clip

Create MIDI clip with generative patterns from chord notes.

```python
create_generative_clip(
    track_index=0,
    clip_index=0,
    chord_notes=[60, 63, 67],  # C minor triad
    pattern_type="arpeggiated",
    rate="1/8",
    direction="up",
    swing=0.0,
    length_beats=4.0,
    velocity_range=(80, 110)
)
```

**Pattern Types:**
- arpeggiated: Converts chord to rhythmic arpeggio using music theory
- random: Randomly selects notes from chord with scale constraints
- strum: Adds chord notes with slight delays for guitar-like effect
- sustained: Holds all chord notes for full duration

**Direction Options:**
- up: Ascending arpeggio
- down: Descending arpeggio
- random: Random order
- up_down: Up then down

**Use Case:** Generate varied patterns from simple chord inputs.

---

### 5. generate_chord_progression_clip

Generate chord progression from Roman numerals.

```python
generate_chord_progression_clip(
    track_index=1,
    clip_index=0,
    key="Fm",
    progression=["i", "VII", "VI", "V"],
    duration_per_chord=4.0,
    voicing="close",
    pattern_type="sustained"
)
```

**Roman Numerals:**
- Major: I, II, III, IV, V, VI, VII
- Minor: i, ii, iii, iv, v, vi, vii
- Case matters: uppercase = major, lowercase = minor

**Voicing Types:**
- close: All notes in same octave
- open: Spread across octaves
- drop2: Drop 2nd highest note down octave

**Pattern Types:**
- sustained: Hold chords for full duration
- arpeggiated: Arpeggiate each chord
- strum: Chord notes with slight delays

**Use Case:** Create harmonic progressions without manual note entry.

---

### 6. generate_melody_clip

Generate scale-constrained melody with complexity control.

```python
generate_melody_clip(
    track_index=2,
    clip_index=0,
    key="F",
    scale="minor",
    length_beats=8.0,
    complexity="medium",
    range_notes=(60, 84)
)
```

**Scale Types:**
- major, minor, dorian, phrygian, lydian, mixolydian

**Complexity Levels:**
- simple: 0.5 notes/beat, quarter note rhythm
- medium: 1.0 notes/beat, quarter/eighth note rhythm
- complex: 2.0 notes/beat, eighth/sixteenth note rhythm

**Range Notes:** (min_pitch, max_pitch) for melody generation

**Use Case:** Create melodic content that fits key.

---

### 7. setup_harmonic_follow_actions

Configure harmonically intelligent follow actions for clip transitions.

```python
setup_harmonic_follow_actions(
    track_index=0,
    clip_range_start=0,
    clip_range_end=7,
    compatibility_mode="moderate",
    stay_probability=0.4
)
```

**Compatibility Modes:**
- strict: Only clips in same key can transition
- moderate: Related keys (relative major/minor, circle of fifths)
- loose: Any clips can transition, weighted toward compatible keys

**Stay Probability:** 0.0-1.0, chance of staying on current clip

**Use Case:** Enable smooth key changes in generative sessions.

---

### 8. setup_energy_based_follow_actions

Configure energy-based follow actions for dynamic progression.

```python
setup_energy_based_follow_actions(
    track_index=0,
    clip_range_start=0,
    clip_range_end=7,
    energy_pattern="build",
    energy_levels=None
)
```

**Energy Patterns:**
- build: Linear increase from energy 1 to 10
- drop: Linear decrease from energy 10 to 1
- cycle: Wave pattern (low-high-low)
- random: Random energy-based transitions

**Energy Levels:** Optional custom list [1-10] per clip

**Use Case:** Create tension/release structures in clip progressions.

---

### 9. create_generative_session

Create complete generative music session with all tracks configured.

```python
create_generative_session(
    genre="dub_techno",
    key="Fm",
    num_tracks=4,
    clips_per_track=8,
    include_drums=True,
    include_bass=True,
    include_chords=True,
    include_melody=True,
    tempo=120
)
```

**Genre Sessions:**
- dub_techno: Fm/Cm key, 120 BPM, minor chords, 1/8 arpeggiation
- house: Am/C key, 125 BPM, major chords, arpeggiated patterns
- techno: Em key, 130 BPM, phrygian scale, heavy velocity
- ambient: F/C key, 80-90 BPM, lydian scale, sustained patterns

**Use Case:** Set up entire generative session in one command.

---

## From Scratch: Full Manual Setup

Step-by-step manual session creation using individual tools.

### Step 1: Clean Slate

```python
delete_all_tracks()
```

### Step 2: Create MIDI Tracks

```python
create_midi_track(0)  # Drums
create_midi_track(1)  # Bass
create_midi_track(2)  # Chords
create_midi_track(3)  # Melody
```

### Step 3: Name Tracks

```python
set_track_name(0, "Drums")
set_track_name(1, "Bass")
set_track_name(2, "Chords")
set_track_name(3, "Melody")
```

### Step 4: Load Instruments

```python
# Drums - Load specific drum kit
load_instrument_or_effect(0, "query:Drums#FileId_58622")

# Bass
load_instrument_or_effect(1, "query:Synths#Bass")

# Chords
load_instrument_or_effect(2, "query:Synths#Electric")

# Melody
load_instrument_or_effect(3, "query:Synths#Operator")
```

### Step 5: Set Tempo

```python
set_tempo(120)
```

### Step 6: Create MIDI Effect Chains

```python
# Drums - No MIDI effects needed (drum kit handles sounds)

# Bass - Scale constraint + Velocity humanization
create_generative_chain(1, "dub_techno", "Fm", False)

# Chords - Scale + Chord + Velocity
create_generative_chain(2, "dub_techno", "Fm", False)

# Melody - Scale + Velocity (ambient style)
create_generative_chain(3, "ambient", "F", False)
```

### Step 7: Generate Clips

```python
# Drums - Use drum pattern generator
create_drum_pattern(0, 0, "one_drop", 4)
create_drum_pattern(0, 1, "steppers", 4)

# Bass - Create generative clips
create_generative_clip(1, 0, [53, 56, 60], "sustained", length_beats=4)
create_generative_clip(1, 1, [53, 56, 60], "arpeggiated", "1/8", "up")

# Chords - Generate progression
generate_chord_progression_clip(2, 0, "Fm", ["i", "VII", "VI", "V"], 4.0)

# Melody - Generate scale-constrained melody
generate_melody_clip(3, 0, "F", "dorian", 8.0, "medium")
```

### Step 8: Configure Follow Actions

```python
# Bass - Harmonic follow actions
setup_harmonic_follow_actions(1, 0, 7, "moderate", 0.4)

# Chords - Energy-based follow actions
setup_energy_based_follow_actions(2, 0, 7, "cycle")

# Melody - Random follow actions
setup_random_follow_actions(3, 0, 7)
```

### Step 9: Start Playback

```python
start_playback()
```

---

## Genre Workflows

### Dub Techno

**Characteristics:** Dark, hypnotic, spacey. Heavy use of echo and reverb.

**Key:** Fm or Cm
**Tempo:** 110-120 BPM

**Setup:**

```python
# Create session
create_generative_session(
    genre="dub_techno",
    key="Fm",
    num_tracks=4,
    clips_per_track=8,
    tempo=120
)

# Or manual setup
delete_all_tracks()
create_midi_track(0)  # Drums
create_midi_track(1)  # Bass
create_midi_track(2)  # Chords
create_midi_track(3)  # Melody

set_track_name(0, "Drums")
set_track_name(1, "Bass")
set_track_name(2, "Chords")
set_track_name(3, "Melody")

load_instrument_or_effect(0, "query:Drums#FileId_58622")
load_instrument_or_effect(1, "query:Synths#Bass")
load_instrument_or_effect(2, "query:Synths#Electric")
load_instrument_or_effect(3, "query:Synths#Operator")

set_tempo(120)

# Create generative clips
create_drum_pattern(0, 0, "one_drop", 4)
create_generative_clip(1, 0, [53, 56, 60], "sustained", length_beats=4)
generate_chord_progression_clip(2, 0, "Fm", ["i", "VII", "VI", "V"], 4.0)
generate_melody_clip(3, 0, "F", "dorian", 8.0, "medium")

# Configure MIDI chains
create_generative_chain(1, "dub_techno", "Fm", False)
create_generative_chain(2, "dub_techno", "Fm", False)
create_generative_chain(3, "ambient", "F", False)

# Follow actions
setup_harmonic_follow_actions(1, 0, 7, "moderate", 0.4)
setup_energy_based_follow_actions(2, 0, 7, "cycle")
setup_random_follow_actions(3, 0, 7)

start_playback()
```

**Tips:**
- Use "one_drop" or "steppers" drum patterns
- Octave-doubled minor chords for depth
- 1/8 arpeggiation for rolling patterns
- Moderate follow actions for harmonic coherence

---

### House

**Characteristics:** Driving, upbeat, rhythmic. Four-on-the-floor kick.

**Key:** Am or C
**Tempo:** 120-125 BPM

**Setup:**

```python
create_generative_session(
    genre="house",
    key="Am",
    num_tracks=4,
    clips_per_track=8,
    tempo=125
)
```

**Manual Pattern:**

```python
# Use major chords
generate_chord_progression_clip(2, 0, "Am", ["I", "VI", "ii", "V"], 4.0)

# Upbeat melodies
generate_melody_clip(3, 0, "A", "major", 8.0, "medium")

# Arpeggiated chords
create_generative_clip(2, 1, [57, 60, 64], "arpeggiated", "1/8", "up")

# Groovy bass
create_generative_clip(1, 0, [45, 48, 52], "arpeggiated", "1/8", "up")
```

**Tips:**
- Major/minor chord progressions
- Arpeggiated chords for rhythmic drive
- 1/8 or 1/16 note density
- Energy-based follow actions: "build" pattern

---

### Techno

**Characteristics:** Driving, hypnotic, repetitive. Four-on-the-floor with heavy synth elements.

**Key:** Em or Dm
**Tempo:** 125-135 BPM

**Setup:**

```python
create_generative_session(
    genre="techno",
    key="Em",
    num_tracks=4,
    clips_per_track=8,
    tempo=130
)
```

**Manual Pattern:**

```python
# Phrygian scale for dark feel
generate_melody_clip(3, 0, "E", "phrygian", 8.0, "complex")

# Driving bass
create_generative_clip(1, 0, [40, 43, 47], "arpeggiated", "1/16", "up")

# Heavy velocity compression
apply_midi_effect_preset(1, "velocity", "dub_heavy")

# Repetitive arpeggios
create_generative_clip(2, 0, [52, 55, 59], "arpeggiated", "1/16", "up")
```

**Tips:**
- Phrygian scale for dark, driving feel
- Heavy velocity (dub_heavy preset)
- 1/16 arpeggiation for intense patterns
- Energy pattern: "build" for tension

---

### Ambient

**Characteristics:** Spacey, atmospheric, evolving. Slow tempos, long reverb tails.

**Key:** F or C
**Tempo:** 70-90 BPM

**Setup:**

```python
create_generative_session(
    genre="ambient",
    key="F",
    num_tracks=3,
    clips_per_track=8,
    tempo=80
)
```

**Manual Pattern:**

```python
# Lydian scale for dreamy feel
generate_melody_clip(2, 0, "F", "lydian", 16.0, "simple")

# Sustained pads
create_generative_clip(1, 0, [53, 57, 60], "sustained", length_beats=8)

# Random humanization
apply_midi_effect_preset(1, "velocity", "random_human")

# Extended chords
generate_chord_progression_clip(0, 0, "F", ["I", "ii7", "V", "I"], 8.0, "close")
```

**Tips:**
- Lydian scale for dreamy textures
- Sustained patterns (not arpeggiated)
- Random velocity for organic feel
- Longer clip lengths (8-16 beats)
- Energy pattern: "cycle" for gentle waves

---

## Prerequisites

### Session Setup Order (Critical)

Always follow this order when creating from scratch:

1. delete_all_tracks() - Clean slate, ensure no audio tracks
2. create_midi_track() - Create MIDI tracks (not audio tracks)
3. set_track_name() - Name tracks for organization
4. load_instrument_or_effect() - Load instruments (never skip this)
5. set_tempo() - Set BPM
6. Create clips/patterns - Now clips will produce sound

**Common Mistakes:**
- Creating clips before loading instruments - Clips will be silent
- Creating clips on audio tracks - Will fail, must use MIDI tracks
- Not loading drum kit preset - Empty Drum Rack has no sounds

### Key Reference

**Format:** Note + "m" for minor, plain note for major

| Key | MIDI Root | Description |
|------|-----------|-------------|
| C | 60 | Major |
| Cm | 60 | Minor |
| F | 65 | Major |
| Fm | 65 | Minor |
| Am | 69 | Minor |
| Em | 64 | Minor |
| D | 62 | Major |
| Dm | 62 | Minor |
| G | 67 | Major |
| Gm | 67 | Minor |

### Scale Types

| Scale | Intervals | Character |
|-------|-----------|-----------|
| major | 0,2,4,5,7,9,11 | Bright, happy |
| minor | 0,2,3,5,7,8,10 | Dark, melancholic |
| dorian | 0,2,3,5,7,9,10 | Jazz, soulful |
| phrygian | 0,1,3,5,7,8,10 | Exotic, Spanish |
| lydian | 0,2,4,6,7,9,11 | Dreamy, floating |
| mixolydian | 0,2,4,5,7,9,10 | Blues, jam band |
| pentatonic_major | 0,2,4,7,9 | Universal, pop |
| pentatonic_minor | 0,3,5,7,10 | Blues, rock |
| blues | 0,3,5,6,7,10 | Blues, jazz |

### Chord Types

| Chord | Intervals | Use Case |
|--------|-----------|-----------|
| major | 0,4,7 | Standard triad |
| minor | 0,3,7 | Minor triad |
| maj7 | 0,4,7,11 | Jazz chord |
| min7 | 0,3,7,10 | Minor seventh |
| dom7 | 0,4,7,10 | Dominant seventh |
| sus2 | 0,2,7 | Suspended 2nd |
| sus4 | 0,5,7 | Suspended 4th |
| power | 0,7 | Rock/metal |

---

## Common Patterns

### Roman Numeral Progressions

**Pop:**
```
["I", "V", "vi", "IV"]
```

**Rock:**
```
["I", "IV", "V"]
```

**Jazz:**
```
["ii", "V", "I"]
```

**Blues:**
```
["I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I"]
```

**EDM:**
```
["i", "V", "vi", "IV"]
```

**Hip-Hop:**
```
["i", "bVI", "bIII", "bVII"]
```

### Dub Techno Progressions

**Classic:**
```
["i", "VII", "VI", "V"]
```

**Dark:**
```
["i", "i", "VII", "i"]
```

**Atmospheric:**
```
["i", "VI", "VII", "i"]
```

---

## Advanced Techniques

### Custom Energy Curves

Create custom energy patterns for specific arrangements:

```python
# Build-up with peak
setup_energy_based_follow_actions(
    track_index=2,
    clip_range_start=0,
    clip_range_end=7,
    energy_levels=[1, 2, 4, 6, 8, 10, 10, 8]
)
```

### Harmonic Compatibility

Use compatibility modes to control key transitions:

**Strict:**
```python
setup_harmonic_follow_actions(
    track_index=0,
    clip_range_start=0,
    clip_range_end=7,
    compatibility_mode="strict"
)
```

**Moderate:**
```python
setup_harmonic_follow_actions(
    track_index=0,
    clip_range_start=0,
    clip_range_end=7,
    compatibility_mode="moderate"
)
```

**Loose:**
```python
setup_harmonic_follow_actions(
    track_index=0,
    clip_range_start=0,
    clip_range_end=7,
    compatibility_mode="loose"
)
```

### Arpeggiation Patterns

**Dub Techno (Rolling):**
```python
create_generative_clip(
    track_index=2,
    clip_index=0,
    chord_notes=[60, 63, 67],
    pattern_type="arpeggiated",
    rate="1/8",
    direction="up",
    swing=0.0
)
```

**Trance (Fast):**
```python
create_generative_clip(
    track_index=2,
    clip_index=0,
    chord_notes=[60, 63, 67],
    pattern_type="arpeggiated",
    rate="1/16",
    direction="random"
)
```

**Ambient (Slow):**
```python
create_generative_clip(
    track_index=2,
    clip_index=0,
    chord_notes=[60, 63, 67],
    pattern_type="arpeggiated",
    rate="1/4",
    direction="random"
)
```

---

## Troubleshooting

### No Sound

**Symptom:** Clips play but no audible output

**Causes:**
- Instrument not loaded
- Track muted
- Volume too low
- Wrong device index in MIDI effect chain

**Solutions:**
```python
# Check track mute
set_track_mute(track_index=0, mute=False)

# Check volume
set_track_volume(track_index=0, volume=0.8)

# Verify instrument loaded
get_track_info(track_index=0)

# Load instrument if missing
load_instrument_or_effect(0, "query:Synths#Bass")
```

### Clips Don't Progress

**Symptom:** Same clip repeats indefinitely

**Causes:**
- Follow actions not configured
- Follow action type set to "None"
- Clip loop disabled

**Solutions:**
```python
# Configure follow actions
setup_harmonic_follow_actions(track_index=0, 0, 7, "moderate")

# Or energy-based
setup_energy_based_follow_actions(track_index=0, 0, 7, "cycle")

# Check follow actions
get_clip_follow_actions(track_index=0, clip_index=0)
```

### Wrong Scale/Key

**Symptom:** Notes sound dissonant or out of key

**Causes:**
- Wrong scale preset applied
- Incorrect key in chord progression
- Scale effect not loaded

**Solutions:**
```python
# Re-apply scale preset
apply_midi_effect_preset(track_index=0, effect_name="scale", preset_name="f_minor")

# Regenerate progression with correct key
generate_chord_progression_clip(track_index=0, clip_index=0, key="Fm", progression=["i", "VII", "VI", "V"])

# Remove scale effect to use all notes
delete_device(track_index=0, device_index=0)
```

### MIDI Effects Not Working

**Symptom:** MIDI effects loaded but no effect on sound

**Causes:**
- Effects loaded in wrong order
- Device index incorrect
- Parameter values not applied

**Solutions:**
```python
# Check device chain order
get_track_info(track_index=0)

# Re-apply preset with correct device index
apply_midi_effect_preset(track_index=0, effect_name="arpeggiator", preset_name="techno_up", device_index=1)

# Load fresh chain
create_generative_chain(track_index=0, chain_type="dub_techno", key="Fm")
```

---

## Reference Tables

### Drum Pattern Presets

| Pattern | Genre | Description |
|---------|--------|-------------|
| one_drop | Reggae | Kick on 3, snare 2&4 |
| rockers | Reggae | Kick on 1&3, snare 2&4 |
| steppers | Dancehall | 4-on-floor kick |
| house_basic | House | Kick on 1, clap on 2&4, hats on all |
| techno_4x4 | Techno | Kick every beat, hats offbeats |
| dub_techno | Dub Techno | Syncopated kick/hat pattern |

### Velocity Presets

| Preset | Drive | Operation | Use Case |
|---------|--------|------------|----------|
| dub_heavy | +20 | compress | Punchy, aggressive |
| dub_soft | -20 | expand | Soft, subtle |
| random_human | 0 | add | Humanized |
| accent_beats | 0 | fixed | Emphasized beats |

### Arpeggiator Styles

| Style | Description | Genre |
|-------|-------------|--------|
| Up | Ascending | All |
| Down | Descending | All |
| UpAndDown | Up then down | Trance |
| Random | Random order | Ambient |
| Pedal | Hold all notes | Ambient |

### Arpeggiator Rates

| Rate | Value | Tempo (BPM) | Note Duration |
|------|--------|---------------|---------------|
| 1/1 | 0.0 | 120 | 0.5s |
| 1/2 | 0.14 | 120 | 0.25s |
| 1/4 | 0.28 | 120 | 0.125s |
| 1/8 | 0.42 | 120 | 0.0625s |
| 1/16 | 0.57 | 120 | 0.03125s |
| 1/32 | 0.71 | 120 | 0.0156s |

---

## Best Practices

### Workflow Order

1. Start with delete_all_tracks() for clean slate
2. Create all MIDI tracks before loading instruments
3. Load instruments immediately after creating tracks
4. Set tempo before creating clips
5. Apply MIDI effect chains before generating clips
6. Generate clips after effects are loaded
7. Configure follow actions last
8. Test playback before finalizing

### Clip Organization

- Use consistent naming: TrackName_Pattern_01, TrackName_Pattern_02
- Organize by energy: Intro, Build, Peak, Drop, Outro
- Group by key: All clips in Fm, all clips in Cm
- Use scene triggers for organized performance

### Instrument Selection

**Drums:**
- Use specific drum kits, not empty Drum Rack
- One Drop/Steppers for dub/reggae
- House beat kits for house music
- Techno kits for 4x4 patterns

**Bass:**
- Operator or Analog for warm bass
- Wavetable for modern bass
- Electric for dub bass

**Chords:**
- Electric or Tension for rich chords
- Wavetable for pad sounds
- Piano or electric piano for house

**Melody:**
- Operator or Wavetable for leads
- Analog for retro sounds
- Sampler for found sounds

### Energy Management

- Start with low energy clips (1-3)
- Build to peak energy (8-10)
- Use follow actions to manage progression
- Drop energy for releases
- Cycle energy for hypnotic sections

---

## Integration with Live Performance

### Clip Launching

```python
# Launch individual clips
fire_clip(track_index=0, clip_index=0)

# Launch scenes
fire_scene(scene_index=0)

# Set quantization for tight timing
set_global_quantization("1 Bar")
```

### Parameter Automation

```python
# Filter sweep for build
apply_filter_buildup(
    track_indices=[2, 3],
    device_index=0,
    parameter_index=0,
    start_value=0.3,
    end_value=0.9,
    duration_beats=16,
    steps=16
)

# Drop effect
apply_drop(
    track_indices=[0, 1],
    device_index=0,
    parameter_index=0,
    drop_value=0.2,
    return_value=0.8,
    drop_instant=True
)
```

### Transposition

```python
# Transpose single clip
transpose_clip(track_index=0, clip_index=0, semitones=2)

# Transpose all playing clips
transpose_all_playing_clips(semitones=2)

# Fire scene with transposition
fire_scene_with_transpose(scene_index=0, semitones=2, exclude_drum_tracks=True)
```

---

## Session Structure Examples

### 8-Bar Loop (Minimal)

```
Clip 0: Intro (bars 1-2)
Clip 1: Verse (bars 3-4)
Clip 2: Build (bars 5-6)
Clip 3: Peak (bars 7-8)
```

### 16-Bar Arrangement (Extended)

```
Clip 0-1: Intro (8 bars)
Clip 2-3: Verse (8 bars)
Clip 4-5: Chorus (8 bars)
Clip 6-7: Bridge (8 bars)
```

### 32-Bar Song Structure (Full)

```
Clip 0-3: Intro (16 bars)
Clip 4-7: Verse A (16 bars)
Clip 8-11: Chorus (16 bars)
Clip 12-15: Verse B (16 bars)
Clip 16-19: Chorus (16 bars)
Clip 20-23: Bridge (16 bars)
Clip 24-27: Final Chorus (16 bars)
Clip 28-31: Outro (16 bars)
```

---

## Next Steps

After creating your generative session:

1. Configure instrument presets in Ableton
2. Set up send routing to return tracks
3. Adjust initial mix levels
4. Test playback with start_playback()
5. Fine-tune parameters and clip patterns
6. Set up follow actions for progression
7. Record or perform live session

---

## Resources

- **MCP Server:** MCP_Server/midi_effects.py - MIDI effect implementations
- **Music Theory:** music_theory/ directory - Chord, scale, progression utilities
- **Live Performance:** docs/live_performance_guide.md - DJ-style techniques
- **Dub Techno:** dub_techno_2h/ directory - 2-hour automation scripts
- **Drum Tools:** scripts/drum_tools/ directory - Drum pattern utilities

---

**For complex automation and long-form sessions, see the Dub Techno 2-Hour project.**
