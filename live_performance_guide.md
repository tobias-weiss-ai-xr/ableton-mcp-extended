# Reggae Live Performance Guide

## Session Overview

**Tempo:** 75 BPM (Classic Roots Reggae)
**Key:** C minor / G minor / F minor progression
**Return Tracks:** A-Reverb, B-Delay

---

## Track Layout

| Track | Name | Instrument | Purpose |
|-------|------|------------|---------|
| 0 | Drums | Drum Rack | Rhythm foundation |
| 1 | Bass | Operator | Sub bass lines |
| 2 | Keys | Audio | (Reserved) |
| 3 | Guitar | Audio | (Reserved) |
| 4 | Horns | Tension | Brass stabs & lines |
| 5 | Extra | Wood Flute | Additional texture |
| 6 | Keys | Electric | Organ skanks |
| 7 | Melody | Wavetable | Hooks & melody |

---

## Clip Library

### Drums (Track 0)

| Slot | Name | Pattern | Use Case |
|------|------|---------|----------|
| 0 | One Drop | Kick on 3, Snare 2&4 | Classic roots, verses |
| 1 | Rockers | Kick on 1, Snare 2&4 | Choruses, full energy |
| 2 | Steppers | 4-on-floor kick | Dancehall, upbeat |
| 3 | Nyabinghi | Heartbeat bass drum | Tribal, spiritual |
| 4 | Dub FX | Sparse, spacey | Breakdowns, transitions |

### Bass (Track 1)

| Slot | Name | Pattern | Use Case |
|------|------|---------|----------|
| 0 | Root Bass | Sustained C | Verses, foundation |
| 1 | Walking Bass | Two-note pattern | Movement, choruses |
| 2 | Dub Bass | Octave jumps | Dub sections |
| 3 | Pulse Bass | Pulsing quarter notes | High energy |

### Keys (Track 6)

| Slot | Name | Chord | Use Case |
|------|------|-------|----------|
| 0 | Cm Skank | C-Eb-G | Main progression |
| 1 | Gm Skank | G-Bb-D | Relative minor |
| 2 | Fm Skank | F-Ab-C | Bridge progression |
| 3 | Dub Chords | Sustained pads | Atmospheric sections |

### Horns (Track 4)

| Slot | Name | Pattern | Use Case |
|------|------|---------|----------|
| 0 | Horn Stabs | C-Eb-G stabs | Accents, hits |
| 1 | Horn Line | Melodic phrase | Hook, response |
| 2 | Horn Swell | Sustained chord | Builds, tension |

### Melody (Track 7)

| Slot | Name | Pattern | Use Case |
|------|------|---------|----------|
| 0 | Guitar Chops | Sparse hits | Rhythm guitar |
| 1 | Melody Hook | Descending line | Main hook |
| 2-3 | (expandable) | | |

---

## Scene Arrangement

| Scene | Name | Suggested Clips |
|-------|------|-----------------|
| 0 | Intro | Drums: Nyabinghi, Bass: Root, Keys: Dub Chords |
| 1 | Verse | Drums: One Drop, Bass: Root, Keys: Cm Skank |
| 2 | Chorus | Drums: Rockers, Bass: Walking, Keys: Gm Skank, Horns: Stabs |
| 3 | Bridge | Drums: One Drop, Bass: Dub, Keys: Fm Skank |
| 4 | Dub Break | Drums: Dub FX, Bass: Dub, Keys: Dub Chords, Horns: Swell |
| 5 | Outro | Drums: Nyabinghi, Bass: Root |

---

## Live Performance Techniques

### 1. DJ-Style Clip Switching (Golden Rule)
```
ONE CLIP CHANGE AT A TIME
```

**Pattern:**
1. Fire drums
2. Wait 4-8 bars
3. Add bass
4. Wait 4-8 bars
5. Add keys
6. Wait 4-8 bars
7. Add horns/melody
8. Repeat with variations

### 2. Filter Sweeps for Builds

| Parameter | Normal | Build | Peak |
|-----------|--------|-------|------|
| Filter | 0.6-0.8 | 0.3-0.5 | 0.8-1.0 |
| Reverb | 0.3 | 0.6 | 0.4 |
| Delay | 0.3 | 0.5 | 0.4 |

### 3. Dub Effects in Real-Time

```python
# Add delay to keys for dub feel
set_send_amount(track_index=6, send_index=1, amount=0.5)

# Add reverb to horns
set_send_amount(track_index=4, send_index=0, amount=0.4)

# Mute/unmute for dramatic effect
set_track_mute(track_index=4, mute=True)  # Mute horns
set_track_mute(track_index=4, mute=False)  # Bring back
```

### 4. Scene-Based Performance

```python
# Trigger entire scenes for section changes
fire_scene(scene_index=0)  # Intro
fire_scene(scene_index=1)  # Verse
fire_scene(scene_index=2)  # Chorus
```

### 5. Parameter Automation

**Dub Bass Drop:**
1. Reduce bass volume: `set_track_volume(track_index=1, volume=0.3)`
2. Wait 2 bars
3. Bring back: `set_track_volume(track_index=1, volume=0.85)`

**Breakdown Build:**
1. Fire "Dub FX" drums
2. Close filters on all instruments
3. Slowly open filters over 8 bars
4. Fire "Rockers" drums at peak

---

## Quick Reference Commands

### Essential Live Commands

```python
# Playback control
start_playback()
stop_playback()

# Clip triggering
fire_clip(track_index=0, clip_index=0)  # One Drop drums
fire_clip(track_index=1, clip_index=0)  # Root Bass
fire_clip(track_index=6, clip_index=0)  # Cm Skank

# Scene triggering
fire_scene(scene_index=1)  # Verse

# Track controls
set_track_volume(track_index=1, volume=0.8)
set_track_mute(track_index=4, mute=True)
set_track_solo(track_index=1, solo=True)

# Effects
set_send_amount(track_index=6, send_index=0, amount=0.5)  # Reverb
set_send_amount(track_index=6, send_index=1, amount=0.4)  # Delay

# Tempo changes (for live feel)
set_tempo(tempo=78)  # Speed up slightly
set_tempo(tempo=72)  # Slow down for dub
```

---

## Reggae Pattern Reference

### One Drop
```
| 1 & 2 & 3 & 4 & |
|     S     K S   |  K=Kick, S=Snare
```

### Rockers
```
| 1 & 2 & 3 & 4 & |
| K   S   K   S   |
```

### Steppers
```
| 1 & 2 & 3 & 4 & |
| K K K K K K K K |  (4-on-floor)
|     S       S   |
```

### Skank (Keys)
```
| 1 & 2 & 3 & 4 & |
|       X       X |  X=Chord on 2&4
```

---

## Performance Workflow

### Standard Song Structure

```
1. INTRO (Scene 0)
   - Nyabinghi drums only
   - Build anticipation

2. VERSE (Scene 1)
   - Full rhythm section
   - No horns yet

3. CHORUS (Scene 2)
   - Add horns
   - Higher energy

4. BRIDGE (Scene 3)
   - Change progression
   - Different feel

5. DUB BREAK (Scene 4)
   - Strip back
   - Heavy effects

6. CHORUS (Scene 2)
   - Full energy return

7. OUTRO (Scene 5)
   - Fade out elements
   - End with drums
```

---

## Troubleshooting

### No Sound
- Check track mute: `set_track_mute(track_index=X, mute=False)`
- Check volume: `set_track_volume(track_index=X, volume=0.8)`
- Verify clip is playing

### Effects Not Working
- Check return track volume
- Verify send amounts are > 0

### Timing Issues
- Use scene triggers for tight changes
- Fire clips on the 1 for best timing
