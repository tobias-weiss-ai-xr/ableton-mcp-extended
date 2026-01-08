# 2-HOUR DUB TECHNOPO - COMPLETE CONFIGURATION GUIDE

## Current Status

✅ **All instruments and effects loaded successfully**

### Session Details
- **Tempo**: 126 BPM
- **Tracks**: 12 total (6 main + 2 sends + 4 existing)
- **MIDI Clips**: 48 clips across 6 tracks
- **Arrangement**: 30 sections (4 minutes each = 2 hours total)

---

## Track Overview

### Main Tracks (4-9)

| Track | Instrument | Effects | Purpose |
|-------|-------------|----------|----------|
| **4 - Kick** | Operator | EQ Eight, Compressor | Punchy 4/4 kick pattern |
| **5 - Sub-bass** | Tension | EQ Eight, Compressor | Deep, hypnotic bass drones |
| **6 - Hi-hats** | Drum Rack | EQ Eight | Sparse, syncopated hi-hats |
| **7 - Synth Pads** | Wavetable | EQ Eight, Auto Filter | Atmospheric chord pads |
| **8 - FX** | Simpler | EQ Eight | Sweeps, impacts, risers |
| **9 - Dub Delays** | - | Utility | Send track for echo effects |

### Send/Return Tracks (10-11)

| Track | Effect | Purpose |
|-------|----------|----------|
| **10 - Reverb Send** | Hybrid Reverb | Returns reverb tails from all tracks |
| **11 - Delay Send** | Simple Delay | Returns dub delays from all tracks |

---

## STEP 1: Configure Instrument Presets

### Track 4 - Kick (Operator)

**Goal**: Create punchy, dub techno kick

**Operator Settings**:
```
Osc A:
  Shape: Sine
  Volume: 0.8
  Transpose: -12 (C2)

Osc B: OFF

Osc C: OFF

Osc D: OFF

Filter:
  Type: Low 24 dB
  Freq: 200-300 Hz
  Res: 0.0

LFO:
  Rate: 1/8 notes
  Amount: 0

Global:
  Volume: Adjust for mix level
  Env: Fast attack, short decay
```

**Envelope**:
```
Attack: 2-5 ms
Decay: 150-200 ms
Sustain: 0
Release: 100-150 ms
```

**Tip**: Add slight saturation on track after Operator for warmth

---

### Track 5 - Sub-bass (Tension)

**Goal**: Deep, hypnotic sub-bass drones

**Tension Settings**:
```
String 1:
  Pick: Bridge
  Damp: 60-80
  Sustain: 80-100
  Level: 0.8
  Detune: 0
  Velo: 50

Filter:
  Type: Low 24 dB
  Freq: 100-150 Hz
  Res: 0.2-0.4

LFO:
  Rate: 1/4 to 1/8 notes
  Target: Filter Freq
  Amount: 20-40%

Global:
  Volume: Adjust for mix level
```

**Envelope**:
```
Attack: 10-20 ms (slow attack for punch)
Decay: 500-1000 ms
Sustain: 0.6-0.8
Release: 500-1000 ms
```

**Tip**: Sidechain this track against kick for groove

---

### Track 6 - Hi-hats (Drum Rack)

**Goal**: Sparse, syncopated hi-hat patterns

**Setup Drum Rack**:
1. Open Drum Rack
2. Load hi-hat samples into chains:
   - Chain 1: Closed hi-hat (velocity 80-100)
   - Chain 2: Open hi-hat (velocity 60-80)
3. Adjust chain volume levels

**Sample Sources**:
- Ableton Core Library: `Drums/Hihat`
- Or use your own hi-hat samples

**Processing**:
```
Chain 1 (Closed):
  Volume: -3 dB
  Pan: Center

Chain 2 (Open):
  Volume: -6 dB
  Pan: Slight stereo spread
```

**Tip**: Add slight compression to hi-hats for consistency

---

### Track 7 - Synth Pads (Wavetable)

**Goal**: Atmospheric, evolving pad sounds

**Wavetable Presets to Try**:
- `Atmospheric Pad`
- `Deep Space`
- `Cinematic Pad`
- `Warm Drone`
- `Ethereal`

**Key Pad Settings**:
```
Oscillator 1:
  Wave: Sine or Triangle
  Level: 0.6
  Detune: 5-10 cents

Oscillator 2:
  Wave: Sine (detuned)
  Level: 0.4
  Detune: 10-15 cents
  Phase: 90 degrees

Filter:
  Type: Low 24 dB
  Cutoff: 800-1200 Hz (automate this!)
  Res: 0.3-0.5
  Keytrack: ON

Effects:
  Chorus: 30-40% wet
  Reverb (send): 40-50%
  Delay (send): 20-30%
```

**Envelope**:
```
Attack: 200-500 ms
Decay: 1-2 seconds
Sustain: 0.8
Release: 2-3 seconds
```

**Auto Filter Automation** (Track 7, Auto Filter device):
```
Frequency: Automate 400-2000 Hz throughout sections
  - Breakdowns: 400-600 Hz (closed)
  - Buildups: Sweep up to 2000 Hz
  - Peaks: 1500-2000 Hz (open)
  - Returns: Sweep down to 800 Hz

LFO:
  Rate: Very slow (1/16 notes)
  Amount: 20-30%
```

---

### Track 8 - FX (Simpler)

**Goal**: Sweeps, impacts, risers

**Load FX Samples**:
1. Open Simpler
2. Load FX samples:
   - Sweep sample (long, rising pitch)
   - Impact sample (short, transient)
   - Noise riser
   - Reverse cymbal

**Sample Sources**:
- Ableton Packs: `FX` folder
- Or your own FX samples

**Processing**:
```
Sweeps:
  Attack: 100-200 ms
  Decay: Full sample length
  Volume: Automate for dramatic effect

Impacts:
  Attack: Fast
  Decay: Short
  Volume: Peak then drop
```

**Tip**: Use different samples for each clip variation

---

### Track 9 - Dub Delays (Send Track)

**Goal**: Capture and echo track signals

**Utility Settings**:
```
Mute: OFF
Mono Mode: OFF (keep stereo)
Gain: 0 dB
```

**This track receives signals via sends from other tracks**

---

## STEP 2: Configure Effects

### EQ Eight (All Tracks 4-8)

**Purpose**: Shape tone and remove unwanted frequencies

**EQ Settings Per Track**:

**Track 4 - Kick**:
```
Low Shelf:
  Freq: 80 Hz
  Gain: +3 dB
  Q: 1.0

Bell 1:
  Freq: 200 Hz
  Gain: -2 dB
  Q: 2.0

High Shelf:
  Freq: 8 kHz
  Gain: -6 dB
  Q: 1.0
```

**Track 5 - Sub-bass**:
```
Low Shelf:
  Freq: 60 Hz
  Gain: +4 dB
  Q: 1.0

Bell 1:
  Freq: 200 Hz
  Gain: -8 dB (cut mud)
  Q: 1.5

High Pass:
  Freq: 150 Hz (remove highs)
  Gain: -∞ dB
  Q: 1.0
```

**Track 6 - Hi-hats**:
```
Low Pass:
  Freq: 300 Hz (remove low rumble)
  Gain: -∞ dB
  Q: 1.0

Bell 1:
  Freq: 8 kHz
  Gain: +3 dB (sparkle)
  Q: 2.0

High Shelf:
  Freq: 12 kHz
  Gain: +2 dB (air)
  Q: 1.0
```

**Track 7 - Synth Pads**:
```
Low Pass:
  Freq: 300 Hz (remove low clutter)
  Gain: -∞ dB
  Q: 1.0

Bell 1:
  Freq: 1.5 kHz
  Gain: -2 dB
  Q: 1.5

High Shelf:
  Freq: 10 kHz
  Gain: +1 dB
  Q: 1.0
```

**Track 8 - FX**:
```
Low Pass:
  Freq: 100 Hz (remove sub)
  Gain: -∞ dB
  Q: 1.0

Bell 1:
  Freq: 2 kHz
  Gain: -1 dB
  Q: 1.5

High Shelf:
  Freq: 15 kHz
  Gain: +2 dB
  Q: 1.0
```

---

### Compressor (Tracks 4-5)

**Purpose**: Add punch and glue

**Track 4 - Kick Compressor**:
```
Threshold: -12 dB
Ratio: 4:1
Attack: 10 ms
Release: 100 ms
Makeup: Auto
```

**Track 5 - Sub-bass Compressor**:
```
Threshold: -15 dB
Ratio: 3:1
Attack: 20-30 ms (slower for sub)
Release: 200-300 ms
Makeup: Auto
```

**Sidechain Setup** (Track 5):
1. Click "Sidechain" button on Compressor
2. Select Track 4 (Kick) as trigger
3. Adjust Threshold for pump/groove

---

### Auto Filter (Track 7)

**Purpose**: Filter automation for evolution

**Auto Filter Settings**:
```
Filter Type: Low 24 dB
Frequency: 400-2000 Hz (AUTOMATE THIS)
Resonance: 0.3-0.5
Drive: Off
Cutoff: Auto
```

**LFO** (in Auto Filter):
```
Rate: 1/16 notes (very slow)
Amount: 25-35%
Retrig: On
```

**Automation Pattern** (see below in Automation section)

---

### Hybrid Reverb (Track 10 - Reverb Send)

**Purpose**: Create atmospheric reverb tails

**Hybrid Reverb Settings**:
```
Size: Large (70-90%)
Decay Time: 3-5 seconds
High Cut: 6 kHz
Low Cut: 200 Hz
Diffusion: 80-90%
Density: 80-90%
Mod Speed: Medium
Mod Depth: Medium
Predelay: 20-40 ms
Early/Late Mix: 50%
```

**Track Level**:
```
Volume: -15 dB (overall reverb level)
```

**Tip**: Use Hybrid Reverb for space and depth

---

### Simple Delay (Track 11 - Delay Send)

**Purpose**: Dub delay echoes

**Simple Delay Settings**:
```
Time: 1/4 or 1/8 notes (dub delay)
Feedback: 35-50% (for repeats)
Filter: Low Pass 4-6 kHz
Dry/Wet: 30-40% wet
```

**Ping Pong Mode** (if available):
```
Mode: Ping Pong
Sync: On
```

**Track Level**:
```
Volume: -12 dB (overall delay level)
```

**Tip**: Adjust Feedback for different delay feels (35-50%)

---

### Utility (Track 9)

**Purpose**: General utility for delays

**Utility Settings**:
```
Mute: OFF
Mono Mode: OFF
Gain: 0 dB
Pan: Center
```

---

## STEP 3: Set Up Send Routing

### Overview

Send routing allows multiple tracks to share reverb and delay effects.

### Send Levels Configuration

For each main track (4-9), create sends to:
- **Track 10 (Reverb Send)** - Send A
- **Track 11 (Delay Send)** - Send B

**Send Levels Per Track**:

**Track 4 - Kick**:
```
Send A (Reverb): 0 (no reverb on kick)
Send B (Delay): 0 (no delay on kick)
```

**Track 5 - Sub-bass**:
```
Send A (Reverb): 0 (no reverb on sub)
Send B (Delay): 5-10% (subtle dub delay)
```

**Track 6 - Hi-hats**:
```
Send A (Reverb): 20-30% (space on hi-hats)
Send B (Delay): 25-35% (hi-hat echoes)
```

**Track 7 - Synth Pads**:
```
Send A (Reverb): 40-50% (maximum reverb)
Send B (Delay): 20-30% (moderate delay)
```

**Track 8 - FX**:
```
Send A (Reverb): 60-70% (lots of reverb tail)
Send B (Delay): 70-80% (dramatic echoes)
```

**Track 9 - Dub Delays**:
```
Send A (Reverb): 80-90% (maximum reverb)
Send B (Delay): 100% (all to delay)
```

### How to Set Up Sends in Ableton

1. **In Session View**, click on track header to expand mixer section
2. For each track (4-9):
   - Click the **Sends** button (A/B)
   - Set **Send A** level to Track 10 (Reverb Send)
   - Set **Send B** level to Track 11 (Delay Send)
   - Use the values above as starting points
3. Adjust levels by ear for your mix

**Tip**: Automate send levels for more dramatic effects during sections

---

## STEP 4: Mix Track Levels

### Target Mix Levels (Master fader at 0 dB)

**Track 4 - Kick**:
```
Volume: -6 to -8 dB
Role: Reference point, punchy but not overwhelming
```

**Track 5 - Sub-bass**:
```
Volume: -3 to -6 dB (relative to kick)
Role: Deep, powerful, sidechained
```

**Track 6 - Hi-hats**:
```
Volume: -12 to -15 dB
Role: Subtle rhythmic accent
```

**Track 7 - Synth Pads**:
```
Volume: -18 to -24 dB
Role: Atmospheric depth, in background
```

**Track 8 - FX**:
```
Volume: -15 to -20 dB
Role: Dramatic accents, not constant
```

**Track 9 - Dub Delays**:
```
Volume: -15 to -18 dB
Role: Echo returns, subtle
```

**Track 10 - Reverb Send**:
```
Volume: -15 dB
Role: Overall reverb return level
```

**Track 11 - Delay Send**:
```
Volume: -12 dB
Role: Overall delay return level
```

### Mixing Procedure

1. **Start with Kick** (Track 4)
   - Set to -6 dB
   - This is your reference

2. **Add Sub-bass** (Track 5)
   - Set to -3 dB relative to kick
   - Adjust until they balance nicely
   - Check for mud/overlap

3. **Add Hi-hats** (Track 6)
   - Set to -12 dB
   - Adjust for subtle presence

4. **Add Synth Pads** (Track 7)
   - Set to -20 dB
   - They should be in background

5. **Add FX** (Track 8)
   - Set to -18 dB
   - They should punctuate, not overwhelm

6. **Adjust Sends** (Tracks 10-11)
   - Balance reverb and delay returns
   - Don't drown the mix

7. **Master Bus Compressor** (on Master track)
   - Add gentle compression (2:1 ratio, -2 dB threshold)
   - Glues everything together

---

## STEP 5: Add Automation

### Filter Automation (Track 7 - Auto Filter)

**Goal**: Create evolving filter sweeps for hypnotic effect

**Automation Strategy**:

**Phase 1: Introduction (Sections 0-3, 0:00-0:16)**
```
Frequency:
  Section 0: 400 Hz (closed filter)
  Section 1: 500 Hz (slightly open)
  Section 2: 600 Hz (opening up)
  Section 3: 800 Hz (more open)
```

**Phase 2: Hypnotic (Sections 4-7, 0:16-0:32)**
```
Frequency:
  Section 4: 800 Hz (stable)
  Section 5: 1000 Hz (subtle shift)
  Section 6: 1200 Hz (opening)
  Section 7: 1000 Hz (closing slightly)
```

**Phase 3: First Build (Sections 8-11, 0:32-0:48)**
```
Frequency:
  Section 8: 1200 Hz (building)
  Section 9: 1500 Hz (opening more)
  Section 10: 2000 Hz (FULLY OPEN - PEAK!)
  Section 11: 1800 Hz (slight close)
```

**Phase 4: Breakdown (Sections 12-15, 0:48-1:04)**
```
Frequency:
  Section 12: 1200 Hz (closing)
  Section 13: 800 Hz (more closed)
  Section 14: 400 Hz (VERY CLOSED - pads disappear)
  Section 15: 600 Hz (re-emerging)
```

**Phase 5: Second Build (Sections 16-19, 1:04-1:20)**
```
Frequency:
  Section 16: 800 Hz (building)
  Section 17: 1200 Hz (opening)
  Section 18: 1600 Hz (more open)
  Section 19: 2000 Hz (PEAK AGAIN!)
```

**Phase 6: Journey Continues (Sections 20-23, 1:20-1:36)**
```
Frequency:
  Section 20: 1500 Hz (sustaining)
  Section 21: 1400 Hz (slight shift)
  Section 22: 1200 Hz (closing)
  Section 23: 1600 Hz (building again)
```

**Phase 7: Final Push (Sections 24-27, 1:36-1:52)**
```
Frequency:
  Section 24: 1800 Hz (opening)
  Section 25: 2000 Hz (MAX PEAK!)
  Section 26: 1900 Hz (sustaining peak)
  Section 27: 1400 Hz (starting release)
```

**Phase 8: Wind Down (Sections 28-29, 1:52-2:00)**
```
Frequency:
  Section 28: 1000 Hz (closing)
  Section 29: 400 Hz (FULLY CLOSED - pads fade out)
```

---

### Reverb Send Automation (Track 10 Sends)

**Goal**: Create more space during breakdowns, less during peaks

**Send A Levels (Reverb)**:

**Phases**:
- **Introduction/Buildups**: 30-40% (moderate)
- **Peaks**: 20-30% (less reverb, more direct)
- **Breakdowns**: 50-60% (LOTS of reverb, pads disappear into space)
- **Returns**: 40-50% (coming back)

**Automation Curve**:
- Use smooth curves (not abrupt jumps)
- Follow section structure (build = less, breakdown = more)

---

### Delay Send Automation (Track 11 Sends)

**Goal**: Create dub echoes during hypnotic sections

**Send B Levels (Delay)**:

**Phases**:
- **Introduction**: 20-25% (subtle echoes)
- **Hypnotic**: 30-40% (more echoes)
- **Buildups**: 35-45% (building echoes)
- **Peaks**: 25-35% (less delay during peak intensity)
- **Breakdowns**: 50-60% (long delays in space)
- **Wind Down**: 30-40% (fading echoes)

---

### Volume Automation (Per Track)

**Purpose**: Add dynamic movement

**Automation Strategy**:

**Track 4 - Kick**:
- Keep mostly consistent (it's the reference)
- Slight boost (+1-2 dB) during peaks
- Return to normal after

**Track 5 - Sub-bass**:
- Consistent during most sections
- Drop 3-6 dB during breakdowns (sub disappears)
- Return during builds

**Track 6 - Hi-hats**:
- Sparse sections: -15 dB (quieter)
- Active sections: -12 dB (louder)
- Breakdowns: Mute (no hi-hats)
- Returns: Back to normal

**Track 7 - Synth Pads**:
- Use volume + filter automation together
- When filter opens, slight volume boost
- When filter closes, volume drops
- Breakdowns: Filter closed, volume reduced

**Track 8 - FX**:
- Muted most of the time
- Unmute briefly for impacts at transitions
- Sudden volume spike then drop (transient)

---

## STEP 6: Final Adjustments

### Frequency Balance

**Check for**:
- **Low-end mud** (below 200 Hz): Cut with EQ on pads and hi-hats
- **Boxiness** (300-500 Hz): Cut on kick or bass
- **Honk/Nasal** (800-1200 Hz): Cut on problematic tracks
- **Harshness** (2-5 kHz): Reduce with high shelf on bright tracks

### Stereo Width

**Synth Pads (Track 7)**:
- Add stereo width effect
- Or pan two oscillators left/right slightly
- Creates wide, atmospheric space

**Reverb/Delays**:
- Use Ping Pong delay for stereo
- Reverb in stereo mode
- Creates 3D depth

### Master Processing

**On Master Track**:
```
Limiter:
  Ceiling: -0.3 dB
  Threshold: Auto
  Release: 100 ms
```

```
Compressor (optional, before limiter):
  Ratio: 2:1
  Threshold: -2 dB
  Attack: 20 ms
  Release: 100 ms
```

---

## STEP 7: Verify and Test

### Playback Test

1. **Start playback** from beginning (Section 0)
2. **Listen to each section transition** (every 4 minutes)
3. **Check for**:
   - Smooth transitions between sections
   - No clipping (check master meters)
   - Balance stays consistent
   - Filter sweeps sound good
   - Reverb/delay levels appropriate

### Sections Check

**Listen for**:
- **Section 10 (Peak Intensity)**: Maximum energy
- **Section 14 (Space)**: Just pads, no rhythm
- **Section 19 (Peak Again)**: High energy returns
- **Section 29 (Fading Out)**: Gradual fade to silence

### Adjustments

If something sounds off:
- **Too muddy**: Cut more low-end from pads/hi-hats
- **Too bright**: Reduce high shelf on bright tracks
- **Not enough punch**: Increase compressor on kick
- **Too much reverb**: Lower reverb send levels
- **Filter sweeps too fast**: Slow down automation

---

## Summary of What You Have

### Structure
✅ **30 sections** x 4 minutes = **2 hours total**
✅ **48 MIDI clips** across 6 tracks
✅ **Full arrangement** with intro, builds, peaks, breakdowns

### Instruments
✅ **Kick**: Operator (punchy)
✅ **Sub-bass**: Tension (deep)
✅ **Hi-hats**: Drum Rack (samples)
✅ **Synth Pads**: Wavetable (atmospheric)
✅ **FX**: Simpler (transients)
✅ **Dub Delays**: Utility (send track)

### Effects
✅ **EQ Eight** on all tracks
✅ **Compressor** on kick and bass
✅ **Auto Filter** on pads (for automation)
✅ **Hybrid Reverb** (send track)
✅ **Simple Delay** (send track)
✅ **Utility** (on delays)

### Next Steps to Complete

1. **Configure presets** on all instruments
2. **Set send levels** for reverb and delay
3. **Mix track volumes** to target levels
4. **Add automation** (filter, sends, volumes)
5. **Test playback** through all 30 sections
6. **Save project** and enjoy your 2-hour dub techno journey!

---

## Quick Reference: Section Timeline

| Time | Section | Energy | Focus |
|-------|----------|---------|
| 0:00-0:04 | 0 | Minimal intro |
| 0:04-0:08 | 1 | Building |
| 0:08-0:12 | 2 | Atmosphere enters |
| 0:12-0:16 | 3 | First movement |
| 0:16-0:20 | 4 | Hypnotic lock |
| 0:20-0:24 | 5 | Subtle shift |
| 0:24-0:28 | 6 | Pad evolution |
| 0:28-0:32 | 7 | Deepening |
| 0:32-0:36 | 8 | Gathering energy |
| 0:36-0:40 | 9 | More movement |
| 0:40-0:44 | 10 | **PEAK INTENSITY** |
| 0:44-0:48 | 11 | Holding pattern |
| 0:48-0:52 | 12 | Thinning out |
| 0:52-0:56 | 13 | Just kick and bass |
| 0:56-1:00 | 14 | **SPACE** (pads only) |
| 1:00-1:04 | 15 | Re-emerging |
| 1:04-1:08 | 16 | Gradual return |
| 1:08-1:12 | 17 | New energy |
| 1:12-1:16 | 18 | Complex layers |
| 1:16-1:20 | 19 | **PEAK AGAIN** |
| 1:20-1:24 | 20 | Deep hypnosis |
| 1:24-1:28 | 21 | Minor shift |
| 1:28-1:32 | 22 | Pad evolution |
| 1:32-1:36 | 23 | Gathering again |
| 1:36-1:40 | 24 | Complex rhythms |
| 1:40-1:44 | 25 | **MAXIMUM MOVEMENT** |
| 1:44-1:48 | 26 | Holding peak |
| 1:48-1:52 | 27 | Beginning release |
| 1:52-1:56 | 28 | Returning to simplicity |
| 1:56-2:00 | 29 | Fading out |

---

**ENJOY YOUR 2-HOUR DUB TECHNOPO JOURNEY!** 🎵

Track is ready for deep, hypnotic listening or DJ sets.
All elements in place - just configure presets, mix, and automate!

Created with AbletonMCP - Natural language control of Ableton Live
