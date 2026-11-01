# STOIC-90 Dub Techno Mixes

## Created: Two 90-Minute Randomized Dub Techno Mixes

Both mixes feature:
- **2700 bars @ 120 BPM** = 90:00 duration
- **7 tracks**: DRUMS, BASS, SUB, CHORDS, PADS, MELODY, FX/PERC
- **7 scenes**: INTRO (180 bars), GROOVE (360), BUILD (180), DROP (720), BREAKDOWN (360), JUMP (360), OUTRO (540)
- **Authentic dub techno bass** with C1/D1/F1/G1 root notes
- **4 automation lanes** with 21,600 automation steps each

---

## Mix 1: Seed 777

**Character**: Deep, hypnotic, subtle variations

### Automation Arcs

| Track | Parameter | INTRO | GROOVE | BUILD | DROP | BREAKDOWN | JUMP | OUTRO |
|-------|-----------|-------|--------|-------|------|-----------|------|-------|
| SUB | Auto Filter Freq | 20%→30% | 30%→40% | 35%→60% | 45%→40% | 45%→20% | 40%→55% | 35%→15% |
| CHORDS | Delay Feedback | 20%→25% | 40%→50% | 50%→65% | 70%→75% | 65%→20% | 50%→55% | 40%→10% |
| CHORDS | Delay Dry/Wet | 25%→30% | 35%→40% | 40%→55% | 60%→65% | 30%→20% | 50%→55% | 30%→15% |
| FX/PERC | Delay Feedback | 15%→20% | 20%→30% | 30%→45% | 50%→65% | 45%→15% | 35%→50% | 25%→8% |

### Randomness (Seed 777)
- Velocity: ±10% spread
- Timing: ±1/16 beat jitter
- Note skipping: 5% probability
- Ghost notes: Random snare/hat/rim at off-beats (scene-dependent)
- Melody: Random pitch selection from alternatives
- Bass: Random octave drops (3%)

**Bass Patterns**:
- INTRO: Long sustained C1 (4 bars)
- GROOVE: Dub one-drop (C1 → G1 on beat 2)
- BUILD: C1 → F1 slide progression
- DROP: Pulsing C1/G1 8th notes
- BREAKDOWN: Walking bass (C1 → F1 → G1)
- JUMP: Octave jumps (C1 → C2 → G1)
- OUTRO: Fading long C1 notes

---

## Mix 2: Seed 2024

**Character**: More variation, energetic, different random trajectories

### Automation Arcs
Same automation templates as Mix 1, but note that:
- The **randomness seed** changes which notes get skipped, velocities, and timings
- The **ghost notes** appear at different positions
- The **melody pitches** vary differently
- The **bass octave drops** occur at different times

### Randomness (Seed 2024)
Same randomness parameters as Mix 1, but with different seed = different variations.

**Differences from Mix 1**:
- Different notes skipped (5% probability per note)
- Different velocity variations (±10%)
- Different timing jitters (±1/16 beat)
- Different ghost note placements
- Different melody pitch selections
- Different bass octave drop timing

---

## Technical Details

### Bass Configuration
- **Pitch Range**: C1 (24), D1 (26), Eb1 (27), F1 (29), G1 (31), Ab1 (32)
- **Instrument**: 101 Essential Bass (FileId_49654)
- **Effects**: EQ Eight + Compressor (for tone shaping)
- **Sub Layer**: Additional bass track with Auto Filter + Saturator

### Drum Patterns
- **INTRO**: Sparse one-drop with ghost notes
- **GROOVE**: Steppers with ghost snares and skank hats
- **BUILD**: Four-on-floor with intensity-building ghost notes
- **DROP**: One-drop with maximum ghost note density
- **BREAKDOWN**: Rim ghost patterns alternating with BD + hats
- **JUMP**: Energetic steppers with triplet feel + ghost notes
- **OUTRO**: Sparse one-drop with fading velocity

### Automations
1. **SUB Track (Track 2)**: Auto Filter Frequency - creates classic dub bass sweeps
2. **CHORDS Track (Track 3)**: Delay Feedback - controls echo intensity
3. **CHORDS Track (Track 3)**: Delay Dry/Wet - controls echo mix
4. **FX/PERC Track (Track 6)**: Delay Feedback - adds texture movement

**Total Automation Steps**: 21,600 per mix

---

## Usage

### Create New Mix
```bash
# Deterministic (no randomness)
python scripts/create_90min_dub_techno.py --fresh --arrange

# Randomized with specific seed (reproducible)
python scripts/create_90min_dub_techno.py --fresh --random --seed 777 --arrange
python scripts/create_90min_dub_techno.py --fresh --random --seed 2024 --arrange

# Randomized with random seed
python scripts/create_90min_dub_techno.py --fresh --random --arrange
```

### Current Mixes in Live
- **Mix 2 (Seed 2024)** is currently loaded in Ableton Live
- Playhead starts at bar 0
- All 49 arrangement clips are placed
- All automations are active

---

## Dub Techno Philosophy Applied

### Minimalism
- Few instruments (7 tracks only)
- Sparse arrangements
- Long, evolving sections (180-720 bars each)
- Subtle automation over time

### Stoic Approach
- No dramatic fills or breaks
- Gradual evolution
- Repetition with small variations
- Hypnotic groove

### Unix Phile Aesthetic
- Clean, functional architecture
- Simple patterns, complex results
- Efficient use of resources
- Deterministic + reproducible randomness

---

## Mix 3: Seed 3333

**Character**: Most variation yet - progressive intensity, evolving patterns

### Enhanced Features

#### Bass Patterns
Each scene now has **unique bass patterns**:
- **INTRO**: Slow walking bass (BA_INTRO + BA_A)
- **GROOVE**: 4-bar rotation (BA_A → BA_B → BA_W → BA_W)
- **BUILD**: Sliding C1 → F1 progression
- **DROP**: Pulsing C1/G1 8th notes
- **BREAKDOWN**: Varied patterns (BA_A → BA_W → BA_B → truncated BA_A)
- **JUMP**: Alternating BA_JUMP + BA_DRIVE
- **OUTRO**: Fading C1/G1 with velocity decay

#### Drum Intensity
- **INTRO**: Minimal (10% ghost, 8% extra hats)
- **GROOVE**: Moderate (20% ghost, 12% extra hats)
- **BUILD**: Progressive (15-45% ghost, 10-30% hats over scene)
- **DROP**: High energy (25-40% ghost, 15-25% hats with fast progression)
- **BREAKDOWN**: Sparse variation (10% ghost)
- **JUMP**: Moderate (20% ghost)
- **OUTRO**: Fading (5% ghost, velocity decay)

#### Melody Evolutions
- **GROOVE**: Call-and-answer with random octave/pitch variations
- **DROP**: Sparse pings with random pitch selection (Bb4, A4, C5)
- **JUMP**: More frequent pings
- **OUTRO**: Slow fading with random pitch selection (G4/A4/Bb4, C5/D5)

### Automation Arcs
Same templates as Mixes 1 & 2, but with:
- More variation in note placement
- Different ghost note positions
- Different random velocities and timings

---

## Summary: Three Unique Dub Techno Mixes

| Mix | Seed | Character | Note Variations | Ghost Notes | Bass Patterns |
|-----|------|-----------|----------------|-------------|---------------|
| 1 | 777 | Deep, hypnotic | Standard | Standard | Basic loop |
| 2 | 2024 | Energetic, balanced | Different | Different | Basic loop |
| 3 | 3333 | Most varied, evolving | Most different | Progressive | Scene-specific |

### What Makes Them Different

1. **Randomness**: Each seed produces different:
   - Which notes are skipped (5% probability)
   - Velocity values (±10% from base)
   - Timing jitter (±1/16 beat)
   - Ghost note placement and density

2. **Bass Patterns** (Mix 3 only):
   - Scene-specific patterns vs. generic loops
   - Progressive complexity in BUILD and DROP
   - Varied BREAKDOWN patterns
   - Alternating JUMP patterns

3. **Drum Intensity** (Mix 3 only):
   - BUILD: Ghost notes increase from 15% to 45% over scene
   - DROP: Fast progression to maximum density
   - Other scenes: Static densities

---

## Current Mix

**Mix 3 (Seed 3333)** is currently loaded in Ableton Live with:
- ✅ 49 arrangement clips (7 per track)
- ✅ 21,600 automation steps
- ✅ All 4 automation lanes active
- ✅ Progressive intensity variations
- ✅ Scene-specific bass patterns
- ✅ Randomized note variations

**Ready to play!** 🎧

Hit play in Ableton to start the 90-minute journey through:**
- INTRO (180 bars) - slow build
- GROOVE (360 bars) - dub one-drop
- BUILD (180 bars) - progressive intensity
- DROP (720 bars) - maximum energy
- BREAKDOWN (360 bars) - sparse variation
- JUMP (360 bars) - rhythmic jump
- OUTRO (540 bars) - gradual fade

---

# EXTREME VERSION: Mix 4 - Maximum Effects & Automation

## 🎛️ Additional Effects per Track

| Track | Original Effects | Additional Effects | Total |
|-------|------------------|-------------------|-------|
| DRUMS | 1 (Drum Buss) | Reverb, EQ Eight | **3** |
| BASS | 2 (EQ8, Comp) | Auto Filter, Saturator | **4** |
| SUB | 2 (Auto Filter, Sat) | Utility | **3** |
| CHORDS | 2 (Delay, Utility) | Auto Filter, Reverb | **4** |
| PADS | 1 (Reverb) | Delay, EQ Eight | **3** |
| MELODY | 2 (Delay, Reverb) | Auto Filter | **3** |
| FX/PERC | 2 (Delay, Reverb) | Auto Filter | **3** |

## 📈 Automation Lanes: 12 Total (68,766 steps!)

### New Automations in EXTREME Version

| # | Track | Parameter | Device | Description |
|---|-------|-----------|--------|-------------|
| 1 | SUB | Frequency | Auto Filter | Filter sweeps (original) |
| 2 | SUB | LFO Rate | Auto Filter | Filter movement speed |
| 3 | SUB | Drive | Saturator | Saturation warmth |
| 4 | BASS | Frequency | Auto Filter | Bass filter cuts |
| 5 | CHORDS | Frequency | Auto Filter | Chord texture filter |
| 6 | CHORDS | Feedback | Delay | Echo intensity (original) |
| 7 | CHORDS | Dry/Wet | Delay | Echo mix (original) |
| 8 | DRUMS | Decay | Reverb | Room size |
| 9 | FX/PERC | Feedback | Delay | FX echo (original) |
| 10 | FX/PERC | Frequency | Auto Filter | FX texture movement |
| 11 | PADS | Decay | Reverb | Space size |
| 12 | PADS | Feedback | Delay | Pad echo texture |
| 13 | MELODY | Frequency | Auto Filter | Lead filter movement |

### Automation Arcs Example (SUB Track)

**Auto Filter on SUB (Track 2)**:
- **Frequency**: 20%→60% across scenes (original dub sweeps)
- **LFO Rate**: 0%→50% - subtle movement in GROOVE, lively in DROP
- **Drive**: 10%→50% - warmth builds through the mix

### Automation Arcs Example (CHORDS Track)

**Auto Filter + Delay + Reverb on CHORDS (Track 3)**:
- **Frequency**: 20%→80% - from subtle to bright
- **Feedback**: 20%→75% - echo intensity (original)
- **Dry/Wet**: 25%→65% - echo mix (original)

### Full Automation Count

| Track | Automation Lanes | Approx. Steps |
|-------|-----------------|---------------|
| SUB | 3 lanes | ~15,000 |
| BASS | 1 lane | ~5,000 |
| CHORDS | 3 lanes | ~15,000 |
| DRUMS | 1 lane | ~5,000 |
| FX/PERC | 2 lanes | ~10,000 |
| PADS | 2 lanes | ~10,000 |
| MELODY | 1 lane | ~5,000 |
| **TOTAL** | **13 lanes** | **68,766** |

---

## Mix 4: Seed 9999

**Character**: EXTREME - Maximum effects, maximum automation, maximum movement!

### What's Different from Mix 3

1. ✅ **More Effects**: Each track has 3-4 effects chain
2. ✅ **More Automation**: 12 automation lanes vs 4
3. ✅ **68,766 automation steps** vs 21,600 (317% more!)
4. ✅ **Deeper Sound**:
   - SUB: Auto Filter + LFO modulation + Saturation Drive
   - BASS: Dedicated Auto Filter for tone shaping
   - CHORDS: Auto Filter + Delay + Reverb combo
   - DRUMS: Reverb Decay automation for space evolution
   - FX/PERC: Auto Filter for textural movement
   - PADS: Delay + Reverb for lush space
   - MELODY: Auto Filter for lead texture

5. ✅ **Progressive Complexity**:
   - INTRO: Minimal effects, subtle automations
   - GROOVE: Moderate automations, movement begins
   - BUILD: Rising complexity, more filter movement
   - DROP: Maximum effects engagement, all automations active
   - BREAKDOWN: Selective reduction, maintaining tension
   - JUMP: Alternating complexity, energy peaks
   - OUTRO: Gradual fade of all effects

---

## Comparison Table

| Feature | Mix 1 | Mix 2 | Mix 3 | Mix 4 EXTREME |
|---------|-------|-------|-------|---------------|
| **Effects/Track** | 1-2 | 1-2 | 1-2 | **3-4** |
| **Automation Lanes** | 4 | 4 | 4 | **12** |
| **Automation Steps** | 21,600 | 21,600 | 21,600 | **68,766** |
| **Bass Patterns** | Loop | Loop | Scene-specific | Scene-specific |
| **Drum Variation** | Basic | Basic | Progressive | Progressive |
| **Randomness** | Yes | Yes | Yes | Yes |
| **Best For** | Clean dub | Balanced | Varied | **Maximum Effects** |

---

## Current Mix

**Mix 4 EXTREME (Seed 9999)** is currently loaded in Ableton Live with:
- ✅ 49 arrangement clips (7 per track)
- ✅ **68,766 automation steps** (12 lanes!)
- ✅ **3-4 effects per track**
- ✅ Progressive intensity variations
- ✅ Scene-specific bass patterns
- ✅ Randomized note variations
- ✅ **Maximum dub techno movement!**

---

## File Reference

- **Standard**: `scripts/create_90min_dub_techno.py`
- **Extreme**: `scripts/create_90min_dub_techno_extreme.py`

## Usage Examples

```bash
# STANDARD version (4 automations, 21.6K steps)
python scripts/create_90min_dub_techno.py --fresh --random --seed 777 --arrange

# EXTREME version (12 automations, 68.7K steps)
python scripts/create_90min_dub_techno_extreme.py --fresh --random --seed 9999 --arrange

# Custom seed
python scripts/create_90min_dub_techno_extreme.py --fresh --random --seed 42 --arrange
```
