# Instrument Selection Guide - Dub Techno Track (Heavy Bass)

## Overview
Since the Ableton MCP Remote Script cannot automatically load instruments, this guide provides detailed recommendations for manual instrument selection and configuration in Ableton Live.

---

## Track-by-Track Instrument Recommendations

### Track 0: Deep Kick

**Recommended:** **Operator** (Kick preset)
**Alternative:** Simpler with kick sample
**Or use:** Analog

#### Why Operator for Dub Techno Kick?
- Punchy, punchy fundamental (40-50 Hz)
- precise pitch control for dub syncopation
- built-in EQ and saturation

#### Manual Setup:
```
1. Click Track 0 device area
2. Press TAB to open Browser
3. Navigate: Instruments → Synth → Operator
4. Load preset: "Kick" or "Fundamental"
5. Adjust:
   - Osc 1: Saw wave, tuned to F (29)
   - Osc 2: Sine, -1 octave (sub layer)
   - Envelope: Fast attack (5ms), quick decay (50-100ms)
   - Volume: 0.80-0.85
   - Add EQ+ after Operator:
     - Low shelf at 80 Hz, +3 dB
     - High pass at 30 Hz (remove sub rumble)
```

#### Key Tuning for Dub Techno:
```
Pattern notes: MIDI 36 (C1) - fundamental
Dub pattern: beats 0, 2.5, 3.0
```

---

### Track 1: Sub-Bass (HEAVY BASS - THE STAR)

**Recommended:** **Operator** (custom patch)
**Alternative:** Wavetable (Sawtooth bass)
**Or use:** Analog

#### This Is The Star Track - HEAVY BASS FOCUS

#### Operator Configuration (Maximum Dub Bass Power):
```
Oscillator 1 (The Foundation):
  Shape: Sawtooth (adds rich harmonics)
  Tune: 0 semitones (root note F = MIDI 29)
  Volume: 0.8
  Detune: 0 (keep it punchy)

Oscillator 2 (The Sub Layer):
  Shape: Sine (pure fundamental)
  Tune: -12 semitones (one octave down)
  Volume: 0.6-0.7 (blend carefully)
  Detune: 0 (tight tracking)

Filter Section:
  Type: Low Pass 24 dB/oct (standard dub filter)
  Frequency: 0.3-0.5 (normalized, ~200-400 Hz) - DUB RANGE!
  Resonance: 0.3-0.5 (moderate resonance for character)
  Drive: 0.2-0.4 (add warmth and harmonics)

Amp Envelope (Sustain heavy):
  Attack: 10-50 ms (short but not clicky)
  Decay: 200-500 ms (let notes breathe)
  Sustain: 1.0 (full sustain for drones)
  Release: 200-500 ms (smooth tails)

LFO (For movement):
  Rate: 0.1-0.5 Hz (slow, hypnotic)
  Destination: Filter Frequency (modulation amount 0.1-0.3)
  Shape: Sine (smooth)
```

#### Effects Chain for HEAVY BASS:
```
Instrument → EQ+ → Compressor → Utility → FX Sends
        [Boost 30-60Hz]   [Gentle]   [Mono]

EQ+ Settings (Critical for Power):
  - Low shelf: 80 Hz, +5 to +7 dB (POWER!)
  - High pass: 30 Hz, 12 dB (remove sub rumble below fundamentals)
  - Low mid: 200 Hz, -2 dB (remove mud)
  - High mid: 800 Hz, -3 dB (focus on sub)

Compressor:
  - Threshold: -18 dB
  - Ratio: 3:1 (gentle but effective)
  - Attack: 5-10 ms
  - Release: 100-200 ms
  - Gain: +3-4 dB (make up for compression)

Utility:
  - Stereo: Mono (keep bass centered!)
  - Pan: 0
  - Volume: 0.85-0.95 (HEAVY!)
```

#### Bass Clip Types & Settings:
```
Sub_F_Drone (Clip 0):
  - Notes: Sustained F (29)
  - Filter: 0.3 (muffled, dark)
  - LFO: Off (steady drone)

Sub_C_Drone (Clip 1):
  - Notes: Sustained C (24)
  - Filter: 0.35
  - Purpose: Relative minor relationship

Sub_F_Pluck (Clip 2):
  - Notes: Quarter-note Fs
  - Attack: 5-10 ms (faster for rhythmic)
  - Filter: 0.4-0.5
  - LFO: On, slow (0.1 Hz)

Sub_Chord_Stab (Clip 3):
  - Notes: F minor triad (29, 32, 36)
  - Duration: 3.5 beats each, every 4 beats
  - Filter: 0.5 (more open)
  - Attack: 5 ms
  - Purpose: Harmonic richness

Sub_Octave_Bounce (Clip 4):
  - Notes: F, octave down, F, octave down...
  - Filter: 0.42
  - Purpose: Thick, powerful

Sub_Cinematic (Clip 5):
  - Notes: Sustained F with velocity layering
  - Filter: Slow mod movement 0.3→0.5→0.3
  - LFO: 0.2 Hz modulation
  - Purpose: Cinematic atmosphere

Sub_Tremolo (Clip 6):
  - Notes: Pulsing quarter notes
  - Amp envelope mod: LFO at 0.5-1 Hz
  - Filter: 0.45
  - Purpose: Rhythmic pulsing

Sub_Reveal (Clip 7):
  - Notes: Long sustained F
  - Filter automation: 0.3 → 0.8 (opening sweep)
  - Length: 8 bars
  - Purpose: Dramatic reveal/breakdown
```

#### Dub Bass Performance Rules:
```
1. ALWAYS check device parameters before setting:
   get_device_parameters(track=1, device=0)

2. NEVER set "Osc On" or "Filter On" to off (mutes track):
   Parameter 0 = Osc 1 On (DON'T TOUCH!)
   Parameter 1 = Osc 2 On (DON'T TOUCH!)
   Parameter 2 = Frequency (SAFE to modulate)
   Parameter 3 = Resonance (SAFE to modulate)

3. Typical Filter Automation Range:
   - Dub/Spacey: 0.3-0.5
   - Normal: 0.5-0.7
   - Builds: 0.4-0.8
   - Peak: 0.75-0.85

4. Volume Automation:
   - Normal: 0.85
   - Builds: 0.90-0.95
   - Breakdowns: 0.70-0.80
```

---

### Track 2: Dub Hats

**Recommended:** **Drum Rack** with hi-hat samples
**Alternative:** Analog (hi-hat synth)
**Or use:** Sampler with multiple hi-hats

#### Manual Setup:
```
1. Click Track 2 device area
2. Press TAB → Instruments → Drums → Drum Rack
3. Load standard hi-hat samples:
   - Closed: C2 (36)
   - Open: D2 (38)
   - Pedal: E2 (40)

Or create from scratch with Analog:
  - White noise generator
  - High pass filter at 8-10 kHz
  - Fast envelope (5-50 ms)
```

#### Drum Rack Pad Mapping:
```
Pad C2 (36) = Closed hat (MIDI 42 in clips)
  - Sample: Short, crisp closed hat
  - Velocity: 60-100

Pad None needed - all hats use same sample
  - Variation via velocity and length in clips
```

#### Effects Chain:
```
Drum Rack → EQ+ → Utility → FX Sends
           [High pass]   [Width]

EQ+:
  - High pass: 1 kHz (remove low mud)
  - Peak: 8 kHz, +2 dB (add shimmer)
  - High shelf: 12 kHz, +3 dB (air)

Utility:
  - Width: 1.2 (spread slightly)
  - Volume: 0.45 (keep subtle!)
```

---

### Track 3: Percs

**Recommended:** **Drum Rack** with percussion samples
**Samples:** Rim, clap, shaker

#### Manual Setup:
```
1. Click Track 3 device area
2. Press TAB → Instruments → Drums → Drum Rack
3. Load samples:

Pad A2 (45) = Rim shot
  - Sample: Sharp rim
  - In clips: MIDI 40

Pad B2 (47) = Clap
  - Sample: Dub clap
  - In clips: MIDI 39

Pad C2 (44) = Shaker
  - Sample: Subtle shaker
  - In clips: MIDI 37
```

#### Effects Chain:
```
Drum Rack → Reverb (return) → Utility → FX Sends
           [Send to track 7]           [Volume]

Utility:
  - Volume: 0.35 (very subtle - textural!)
  - Pan: Variable per perc type
```

---

### Track 4: Atmo Pad

**Recommended:** **Wavetable**
**Alternative:** Analog
**Or use:** Collision

#### Why Wavetable for Dub Pads?
- Rich, evolving textures
-extensive modulation options
- Dark, cinematic sounds

#### Manual Setup (Dark Dub Pad):
```
Oscillator 1:
  Wave: Dark Saw or Square
  Frequency: Root note centered
  Detune: 0
  LFO: Slow movement (0.1-0.3 Hz)

Oscillator 2:
  Wave: Another dark waveform (detuned)
  Detune: -3 to +3 cents (unison detune)
  LFO: Independent modulation

Filter:
  Type: Low Pass 24 dB
  Frequency: 0.2-0.5 (normalized) - VERY DUB!
  Resonance: 0.2-0.4
  LFO: Slow sweep (0.05-0.1 Hz)

Amp Envelope:
  Attack: 50-200 ms (slow, atmospheric)
  Decay: Long (500 ms - 2 sec)
  Sustain: 0.6-0.8
  Release: 500-2000 ms (long tails)

Effects (atmosphere):
  - Chorus: 30-50% mix, slow rate
  - Reverb Send: 0.5-0.7 (to Track 7)
```

#### Pad Chord Clip Types:
```
Pad_Fm_Sustain (Clip 0):
  - Chord: F minor (29, 32, 36) - DARK!
  - Filter: 0.25
  - Reverb: 0.6

Pad_Cm_Sustain (Clip 1):
  - Chord: C minor (24, 27, 31)
  - Purpose: Relative minor

Pad_Bb_Sustain (Clip 2):
  - Chord: Bb minor (22, 25, 29)
  - Purpose: Pre-dominant

Pad_Fm_Movement (Clip 3):
  - Chord: F minor with LFO filter sweep
  - Filter: 0.2→0.4→0.2 over 8 bars
  - Purpose: Evolving

Pad_Drones (Clip 4):
  - Single: F organ pedal (29)
  - Filter: Very low (0.2)
  - Purpose: Deepest atmosphere

Pad_None (Clip 5):
  - Silence (remove pad)

Pad_Dub_Wash (Clip 6):
  - Chord: F minor
  - Delay: 0.6-0.8 (send to Track 6)
  - Reverb: 0.8
  - Purpose: Heavy dub wash

Pad_Peak (Clip 7):
  - Chord: F minor
  - Filter: 0.6 (more open)
  - Reverb: 0.8
  - Purpose: Peak section
```

---

### Track 5: Dub FX

**Recommended:** **Simpler** with FX samples
**Alternative:** Drum Rack with FX sounds
**Or use:** Sampler with multi-zone mapping

#### Manual Setup:
```
1. Click Track 5 device area
2. Press TAB → Instruments → Simpler
3. Load FX samples from library:

NOISE SWELL (FX_Noise_Swell - Clip 1):
  - Load: White noise sample
  - ADSR: Long attack, long decay
  - Filter: Low pass, automate opening
  - Clip notes trigger ascending chromatic

REVERB IMPACT (FX_Reverb_Impact - Clip 2):
  - Load: Metallic impact/boom
  - Add: Reverb effect after Simpler
  - Clip: Sharp hit + sustaining tail

DELAY BOOM (FX_Delay_Boom - Clip 3):
  - Load: Sub boom/sample
  - Add: Delay effect
  - Clip: Single hit with echo notes

FILTER SWEEP (FX_Filter_Sweep - Clip 4):
  - Load: Filter sweep sample or synth
  - Or: Pink noise with filter automation
  - Clip: Descending notes

METALLIC (FX_Metallic - Clip 5):
  - Load: Industrial hits/clang
  - Clip: Short sharp hits

RISER (FX_Riser - Clip 6):
  - Load: Pitch riser sample
  - Or: White noise with pitch envelope
  - Clip: Ascending chromatic

GLITCH (FX_Glitch - Clip 7):
  - Load: Glitch percussion
  - Clip: Random rhythmic pattern
```

#### Alternative - Use Ableton's Built-in Instruments:
```
Instead of samples, use:

Collision (FM percussion):
  - Create unique metallic hits
  - Simpler than loading samples

Operator (FX synthesis):
  - White noise + filter automation
  - Create custom effects

Analog (analog FX):
  - Filter sweeps from noise
  - Classic dub feel
```

---

### Track 6: Dub Delay (Send Track - Audio)

**Recommended:** **Simple Delay**
**Alternative:** Ping Pong Delay
**Or use:** Glitch (advanced)

#### Manual Setup (The Classic Dub Delay):
```
1. Click Track 6 device area (it's an audio track)
2. Press TAB → Audio Effects → Signal → Delay → Simple Delay

Simple Delay Settings (Dub Perfection):
  - Sync: 1/4 note (classic dub quarter note echo)
  - Sync: 1/8 (for faster builds - optional)
  - Feedback: 50-60% (1+ echoes)
  - Dry/Wet: 70-80% (mostly delay)
  - Filter: Low pass at 4-6 kHz (dampen repeats)
  - Volume: 0.50 (send track volume)

Optional: Add Ping Pong Delay after Simple Delay
  - Sync: 1/8
  - Feedback: 30-40%
  - Creates width and movement
```

#### Send Routing Setup (Manual in Ableton Mixer):
```
For each track (0-5), add sending to Track 6:

Track 0 (Deep Kick):
  - Send 6 (Dub Delay): 0 (kicks shouldn't echo)

Track 1 (Sub-Bass):
  - Send 6: 0.2-0.4
  - Purpose: Sub trickles on stabs
  - Don't overdo - keeps bass tight

Track 2 (Dub Hats):
  - Send 6: 0.3-0.5
  - Purpose: Dub echo on hats

Track 3 (Percs):
  - Send 6: 0.4-0.6
  - Purpose: Percussion echoes

Track 4 (Atmo Pad):
  - Send 6: 0.4-0.6
  - Purpose: Pad washes

Track 5 (Dub FX):
  - Send 6: 0.6-0.8
  - Purpose: FX trails
```

---

### Track 7: Reverb (Send Track - Audio)

**Recommended:** **Hybrid Reverb**
**Alternative:** Reverb (simple)
**Or use:** Convolution Reverb

#### Manual Setup (Deep Dub Reverb):
```
1. Click Track 7 device area (audio track)
2. Press TAB → Audio Effects → Reverb → Hybrid Reverb

Hybrid Reverb Settings (Cavernous Space):
  - Size: Large (Big)
  - Decay Time: 2-4 seconds (LARGE TAIL)
  - High Cut: 6-8 kHz (soften high end)
  - Low Cut: 80 Hz (remove low mud)
  - Pre-Delay: 20-50 ms (slap-back echo)
  - Dry/Wet: 60-70% (mostly wet)
  - Volume: 0.60 (send track volume)

Alternative: Simple Reverb (if Hybrid unavailable)
  - Decay Time: 3-4 sec
  - High Cut: 6 kHz
  - Density: High
  - Size: Big
  - Stereo Width: Wide
```

#### Send Routing Setup (Manual in Ableton Mixer):
```
For each track (0-5), add sending to Track 7:

Track 0 (Deep Kick):
  - Send 7 (Reverb): 0 (keep kick punchy)

Track 1 (Sub-Bass):
  - Send 7: 0.0-0.2 (minimal - bass loses power with reverb)
  - Purpose: Subtle space only

Track 2 (Dub Hats):
  - Send 7: 0.3-0.5
  - Purpose: Hat space

Track 3 (Percs):
  - Send 7: 0.3-0.5
  - Purpose: Perc ambience

Track 4 (Atmo Pad):
  - Send 7: 0.5-0.7 (HEAVY)
  - Purpose: Pads live here!

Track 5 (Dub FX):
  - Send 7: 0.6-0.8 (MAX)
  - Purpose: Atmosphere and space
```

---

## Quick Reference Cheat Sheet

### Track 0 - Deep Kick
- **Instrument:** Operator (Kick preset)
- **Tuning:** MIDI 36 (C1)
- **Power:** First attack, sub layer
- **Effects:** EQ+ (boost 80 Hz), Compressor

### Track 1 - Sub-Bass (THE STAR)
- **Instrument:** Operator (custom)
- **Osc 1:** Sawtooth, F (29), volume 0.8
- **Osc 2:** Sine, -1 octave, volume 0.65
- **Filter:** Low Pass 24dB, 0.3-0.5 range
- **Effects:** EQ+ (boost 30-60 Hz +7 dB), Compressor, Utility (MONO)
- **Volume:** 0.85-0.95 (HEAVY!)

### Track 2 - Dub Hats
- **Instrument:** Drum Rack
- **Samples:** Closed hat (MIDI 42)
- **Effects:** EQ+ (high pass 1 kHz)
- **Volume:** 0.45

### Track 3 - Percs
- **Instrument:** Drum Rack
- **Samples:** Rim (40), Clap (39), Shaker (37)
- **Volume:** 0.35

### Track 4 - Atmo Pad
- **Instrument:** Wavetable
- **Filter:** Low Pass, 0.2-0.5 (very dark)
- **LFO:** Slow (0.1-0.3 Hz)
- **Sends:** Delay 0.5, Reverb 0.7

### Track 5 - Dub FX
- **Instrument:** Simpler
- **Samples:** Load FX library
- **Or:** Use Collision for synthesis

### Track 6 - Dub Delay (Send)
- **Effect:** Simple Delay
- **Sync:** 1/4
- **Feedback:** 50-60%
- **Sends:** From Tracks 1-5 (see above)

### Track 7 - Reverb (Send)
- **Effect:** Hybrid Reverb
- **Decay:** 2-4 seconds
- **Size:** Large
- **Sends:** From Tracks 2-5 heavily, Track 1 lightly

---

## Setup Time Estimates

| Task | Time |
|------|------|
| Track 0: Kick instrument | 5 min |
| Track 1: Sub-Bass configuration | 20 min |
| Track 2: Drum Rack hats | 5 min |
| Track 3: Drum Rack percs | 5 min |
| Track 4: Wavetable pad | 10 min |
| Track 5: FX samples | 15 min |
| Track 6: Delay + sends | 10 min |
| Track 7: Reverb + sends | 10 min |
| Fine-tune all sounds | 30 min |
| **Total** | **110 min (approx 2 hours)** |

---

## Next Steps After Instrument Loading

1. **Test all clips:** Fire each clip to verify sounds work
2. **Adjust MIDI notes:** Clip notes may need transposition
3. **Configure drum racks:** Map samples to correct MIDI notes
4. **Set up sends:** In Ableton mixer, add sends to Tracks 6 & 7
5. **Balance levels:** Adjust using utility and volume faders
6. **Test transitions:** Try clip switches with parameter sweeps

---

**End of Instrument Guide**

Total pages: ~13 lines
Tracks covered: 8 complete
Focus: Heavy dub bass power
Estimated setup time: 2 hours