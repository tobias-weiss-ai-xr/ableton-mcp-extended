# 🎵 **FAT BEATZ SUITE** - Maximum Thickness & Punch

> **"Dub taught us bass and effects are key. Fat Beatz takes it further."**

This module provides **production-grade tools** for creating thick, punchy, bass-heavy beats with professional processing chains. It's designed for producers who want **studio-quality fatness** without the manual tweaking.

---

## 🚀 **QUICK START**

```python
# Create a complete fat beat in one call
create_fat_beat(
    bpm=95.0,
    bars=8,
    kick_pattern="X---|----|X---|----",
    snare_pattern="----|X---|----|X---",
    hat_pattern="--x-|--x-|--x-|--x-",
    bass_octave=0,
    bass_pattern="X---|----|X---|----",
    add_compression=True,
    add_saturation=True,
    add_sidechain=True,
    bass_enhancement="parallel",
    stereo_widening="haas"
)
```

This creates:
✅ 5 tracks (kick, snare, hi-hat, bass, returns)
✅ Professional drum programming
✅ Bassline with your pattern
✅ Parallel compression on bass
✅ Saturation on all drums
✅ Sidechain from bass to non-bass elements
✅ Haas-effect stereo widening on hats/snare

---

## 📚 **TOOL CATEGORIES**

### 🔥 **1. BASS ENHANCEMENT** (The Foundation of Fatness)

#### `add_sub_bass_harmonic`
Adds an **octave-shifted sub-bass** to thicken thin basslines:
```python
add_sub_bass_harmonic(
    track_index=0,           # Your bass track
    harmonic_octave=-1,      # One octave down (sub)
    harmonic_volume=0.5,     # 50% volume relative to original
    filter_cutoff=150,       # LP filter to remove mud
    saturation_amount=0.3    # Analog warmth
)
```

**What it does:**
- Creates a new audio track
- Pitch-shifts your bass down an octave
- Applies low-pass filter (removes high-frequency noise)
- Adds subtle saturation
- Blends with original

**Pro Tips:**
- Use `harmonic_octave=-2` for **sub-sub** bass (extreme low end)
- Reduce `filter_cutoff` to 80-100Hz for cleaner sub
- Increase `saturation_amount` to 0.5-0.7 for more analog character

---

#### `boost_bass_frequencies`
Surgically boosts **bass frequencies** using EQ:
```python
boost_bass_frequencies(
    track_index=0,
    boost_db=6.0,          # +6dB boost
    center_frequency=80,   # Center on 80Hz
    q_factor=1.5           # Medium bandwidth
)
```

**Frequency Guide:**
| Frequency | Effect | Boost Amount |
|-----------|--------|--------------|
| 40-50Hz | Sub-bass fundamental | +4 to +8dB |
| 60-80Hz | Weight and body | +3 to +6dB |
| 100-150Hz | Fullness | +2 to +4dB |
| 200-300Hz | Warmth | +1 to +3dB |

**Pro Tips:**
- Use **lower Q (0.5-1.0)** for wider, smoother boosts
- Use **higher Q (2.0-3.0)** for targeted, surgical boosts
- Check for **mud** in the 200-500Hz range - cut if necessary

---

#### `create_parallel_bass_compression`
NY-style **parallel compression** for punch and sustain:
```python
create_parallel_bass_compression(
    track_index=0,
    compression_amount=0.5,  # 50% compressed signal
    attack_ms=10,           # Fast attack = preserves transients
    release_ms=100,         # Medium release = natural sustain
    ratio=4.0,              # 4:1 ratio = good balance
    threshold_db=-12        # Catch all but quietest notes
)
```

**What it does:**
1. Duplicates your bass track
2. Applies **heavy compression** to the duplicate
3. Blends it back with the original
4. Result: **Transients preserved + body/sustain added**

**Compression Settings for Different Styles:**

| Style | Attack | Release | Ratio | Threshold |
|-------|--------|---------|-------|-----------|
| Punchy House | 5-15ms | 50-100ms | 4:1-6:1 | -12 to -18dB |
| Smooth R&B | 20-30ms | 100-200ms | 2:1-4:1 | -15 to -20dB |
| Dub | 30-50ms | 200-300ms | 3:1-5:1 | -18 to -24dB |
| Trap | 1-10ms | 20-80ms | 6:1-8:1 | -20 to -30dB |

**Pro Tips:**
- Start with `compression_amount=0.3-0.5` and adjust to taste
- For **more punch**, use faster attack (5-10ms)
- For **more sustain**, use slower release (150-300ms)
- Use **higher ratio** (6:1-8:1) for aggressive compression
- Use **lower ratio** (2:1-3:1) for subtle gluing

---

### 🥁 **2. DRUM FATNESS** (Make It Knock)

#### `enhance_kick_drum`
Complete **kick drum enhancement** with multiple techniques:
```python
enhance_kick_drum(
    track_index=0,
    add_click=True,        # Layer click sample for attack
    click_volume=0.3,      # Click sample volume
    boost_attack=True,     # Boost high frequencies
    attack_db=12,          # +12dB at 8kHz
    extend_tail=True,      # Enhance low end
    tail_hz=40,            # Boost at 40Hz
    saturation_drive=0.5   # Analog warmth
)
```

**What it does:**
- ✅ Adds **click layer** for snap (sample-based)
- ✅ Boosts **attack** at 5-10kHz for punch
- ✅ Extends **tail** at 40-80Hz for weight
- ✅ Adds **saturation** for analog character

**Pro Tips:**
- For **Acoustic/Electro House**: `attack_db=10-14`, `tail_hz=50-60`
- For **EDM/Trap**: `attack_db=12-16`, `tail_hz=40-50`
- For **Techno/Hip-Hop**: `attack_db=8-12`, `tail_hz=30-40`
- Try `click_volume=0.2-0.4` for subtle click
- Try `click_volume=0.5-0.7` for obvious click

---

#### `thicken_snare`
Professional **snare thickening** with multiple layers:
```python
thicken_snare(
    track_index=1,
    parallel_reverb=True,   # Add reverb on parallel bus
    reverb_decay=0.5,       # 500ms decay
    reverb_mix=0.3,         # 30% wet in parallel
    add_body=True,          # Boost mid frequencies
    body_freq=200,          # 200Hz for body
    body_db=6,              # +6dB boost
    gate_threshold=-20,     # Gate out noise
    saturation=0.4          # Analog warmth
)
```

**What it does:**
- ✅ Adds **parallel reverb** for space
- ✅ Boosts **body** at 150-250Hz for thickness
- ✅ Adds **noise gate** to remove ring
- ✅ Adds **saturation** for character

**Snare Body Frequencies:**
| Frequency | Effect | Instrument Type |
|-----------|--------|-----------------|
| 100-150Hz | Weight | Hip-Hop, Trap |
| 150-200Hz | Body | House, Techno |
| 200-250Hz | Fullness | Pop, R&B |
| 250-350Hz | Snap | Snappy Pow |

**Pro Tips:**
- For **Trap**: `body_freq=120-150`, `body_db=6-8`
- For **House**: `body_freq=180-220`, `body_db=4-6`
- For **Pop**: `body_freq=200-250`, `body_db=3-5`
- Use `reverb_decay=0.3-0.7` for nice snap
- Use `reverb_decay=0.8-1.5` for big room sound

---

### 🎚️ **3. MIX FATNESS** (Make It Wide)

#### `apply_stereo_widening`
Widen your **stereo image** for dimension:
```python
apply_stereo_widening(
    track_index=2,        # Hi-hat track
    method="haas",        # Haas effect (delay one side)
    width_percent=100,    # Full width
    high_pass_hz=200,     # Keep low end mono
    delay_ms=25           # 25ms delay for Haas
)
```

**Widening Methods:**

| Method | How it Works | Best For | Mono Compatibility |
|--------|-------------|----------|---------------------|
| `"haas"` | Delay one side by 10-30ms | Hi-hats, cymbals | ⚠️ Phase issues if >30ms |
| `"mid_side"` | Process mid and side separately | Pads, synths | ✅ Excellent |
| `"chorus"` | Chorus effect with subtle settings | Guitars, vocals | ✅ Good
**Delay Times for Haas Effect:**
| Delay (ms) | Perceived Width | Mono Compatibility |
|------------|-----------------|---------------------|
| 5-15ms | Subtle | ✅ Very Good |
| 15-25ms | Moderate | ✅ Good |
| 25-30ms | Wide | ⚠️ Be careful |
| 30-50ms | Very Wide | ❌ Phase issues |

**Pro Tips:**
- **Always keep low frequencies mono** (use `high_pass_hz=150-300`)
- For **hi-hats**: `width_percent=50-70`, `delay_ms=15-25`
- For **pads**: `method="mid_side"`, `width_percent=80-100`
- For **vocals**: `width_percent=20-30` (keep centered)
- **Check in mono** - widening should collapse to mono without issues

---

#### `add_harmonic_excitement`
Add **upper harmonics** to make sounds more present:
```python
add_harmonic_excitement(
    track_index=0,        # Bass track
    mode="tape",          # Tape-style saturation
    drive=0.5,            # 50% saturation
    output=0.0,           # No output boost
    high_pass=100,        # HP filter before saturation
    low_pass=12000        # LP filter before saturation
)
```

**Saturation Modes:**

| Mode | Character | Best For |
|------|-----------|----------|
| `"tape"` | Even harmonics, warm | Bass, vocals, pads |
| `"tube"` | Odd harmonics, aggressive | Drums, guitars |
| `"digital"` | Bright, clean | High synths, leads |
| `"bitcrush"` | Lo-fi, gritty | Special effects, risers |

**Drive Settings:**
| Drive | Effect | Use Case |
|-------|--------|----------|
| 0.1-0.2 | Subtle | Master bus |
| 0.2-0.4 | Noticeable | Individual tracks |
| 0.4-0.6 | Strong | Drum parallel |
| 0.6-0.8 | Aggressive | Special effects |
| 0.8-1.0 | Distorted | Sound design |

**Pro Tips:**
- **Bass**: Use `mode="tape"`, `drive=0.3-0.5`, `high_pass=80-100`
- **Drums**: Use `mode="tube"`, `drive=0.4-0.7`, `high_pass=100-150`
- **Vocals**: Use `mode="tape"`, `drive=0.2-0.4`, `high_pass=200-300`
- **Master**: Use `mode="tape"`, `drive=0.1-0.2`, `high_pass=300-500`
- **Always use filters** to avoid muddying low end

---

### 🎛️ **4. SIDECHAIN PUMPING** (Make It Breathe)

#### `setup_sidechain_pump`
Create **sidechain compression** for that pumping effect:
```python
setup_sidechain_pump(
    source_track=3,          # Bass track (trigger)
    target_tracks=[2, 4],    # Hi-hat and pad tracks
    compressor_threshold=-24,
    compressor_ratio=4.0,
    compressor_attack=10,
    compressor_release=100,
    sidechain_amount=0.5,
    key_input_gain=6.0
)
```

**What it does:**
1. Uses bass track as **sidechain input**
2. Triggers compressor on **target tracks**
3. Each bass hit **ducks** the target tracks
4. Creates **rhythmic pumping** effect

**Sidechain Release Times by Tempo:**
| BPM | Release (ms) | Effect |
|-----|--------------|--------|
| 60-80 | 200-400 | Slow, atmospheric |
| 80-100 | 150-250 | Groovy |
| 100-120 | 100-150 | Punchy |
| 120-130 | 80-120 | House |
| 130-140 | 50-100 | Techno |
| 140+ | 20-80 | Fast, aggressive |

**Release Formula:**`
```
16000 / (BPM * 4) = Quarter note in ms
Example: 128 BPM → 16000 / 512 = 31.25ms per quarter note
```

**Pro Tips:**
- For **EDM**: `compressor_release=50-150ms`, `ratio=4:1-6:1`
- For **House**: `compressor_release=80-120ms`, `ratio=3:1-5:1`
- For **Trap**: `compressor_release=20-80ms`, `ratio=6:1-8:1`
- Use `sidechain_amount=0.3-0.5` for subtle pumping
- Use `sidechain_amount=0.7-1.0` for dramatic effect
- **Match release to tempo** for rhythmic pumping

---

### 📀 **5. MASTERING** (Make It Loud)

#### `maximize_loudness`
Bring up **overall level** while preserving dynamics:
```python
maximize_loudness(
    track_index=0,          # Master track
    ceiling_db=-0.3,       # Don't exceed -0.3dB
    loudness_target=-8.0,  # Target -8 LUFS
    release_ms=50,         # Release time
    lookahead_ms=5,        # Lookahead time
    gain_boost=3.0         # Initial gain boost
)
```

**Loudness Targets by Genre:**
| Genre | LUFS Range | Notes |
|-------|------------|-------|
| Classical | -23 to -14 | Very dynamic |
| Jazz | -20 to -14 | Dynamic |
| Rock | -14 to -8 | Moderate compression |
| Pop | -12 to -8 | Compressed |
| Hip-Hop | -10 to -7 | Very compressed |
| EDM | -9 to -6 | Max loudness |
| Club | -8 to -5 | Loudest |

**Pro Tips:**
- Start with `ceiling_db=-0.1` to be safe
- `loudness_target=-8` is good for most electronic music
- Use `release_ms=20-100` for transparency
- Use `lookahead_ms=2-10` to catch transients
- **Check with a LUFS meter** - these are starting points
- Leave **headroom** for mastering engineer

---

## 🎯 **COMPLETE WORKFLOWS**

### Workflow 1: **Fat Bassline**
```python
# Step 1: Create bass track with sub
add_sub_bass_harmonic(track_index=0, harmonic_octave=-1, harmonic_volume=0.4)

# Step 2: Boost bass frequencies
boost_bass_frequencies(track_index=0, boost_db=4, center_frequency=60, q_factor=1.2)
boost_bass_frequencies(track_index=0, boost_db=3, center_frequency=120, q_factor=1.8)

# Step 3: Add parallel compression
create_parallel_bass_compression(
    track_index=0,
    compression_amount=0.6,
    attack_ms=10,
    release_ms=150,
    ratio=5.0
)

# Step 4: Add harmonic excitement
add_harmonic_excitement(
    track_index=0,
    mode="tape",
    drive=0.4,
    high_pass=80
)
```

---

### Workflow 2: **Punchy Drums**
```python
# Kick
enhance_kick_drum(
    track_index=0,
    add_click=True,
    click_volume=0.35,
    boost_attack=True,
    attack_db=14,
    extend_tail=True,
    tail_hz=45
)

# Snare
thicken_snare(
    track_index=1,
    parallel_reverb=True,
    reverb_decay=0.6,
    reverb_mix=0.25,
    add_body=True,
    body_freq=180,
    body_db=5
)

# Hi-Hat stereo widening
apply_stereo_widening(
    track_index=2,
    method="haas",
    width_percent=75,
    high_pass_hz=200,
    delay_ms=20
)
```

---

### Workflow 3: **Full Fat Beat with Automation**
```python
# Create complete beat
result = create_fat_beat(
    bpm=95,
    bars=8,
    kick_pattern="X---|----|X---|----",
    snare_pattern="----|X---|----|X---",
    hat_pattern="--x-|--x-|--x-|--x-",
    bass_octave=0,
    bass_pattern="X---|----|X---|----",
    add_compression=True,
    add_saturation=True,
    add_sidechain=True,
    bass_enhancement="parallel",
    stereo_widening="haas",
    loudness_maximization=True
)

# Then enhancements
boost_bass_frequencies(track_index=3, boost_db=5, center_frequency=70)
enhance_kick_drum(track_index=0, saturation_drive=0.6)
thicken_snare(track_index=1, reverb_decay=0.8)
```

---

### Workflow 4: **Dub + Fat Beatz Hybrid**
```python
# Create dub arrangement with fat elements
from MCP_Server.arrangement_tools import create_dub_arrangement

# Create dub structure
create_dub_arrangement(
    sections=[
        {"name": "Intro", "scene_index": 0, "bars": 16, "is_dub_drop": False},
        {"name": "Verse", "scene_index": 1, "bars": 16, "unique_bassline": True},
        {"name": "Drop", "scene_index": 2, "bars": 32, "is_dub_drop": True, "unique_bassline": True},
        {"name": "Breakdown", "scene_index": 3, "bars": 16, "is_breakdown": True},
    ],
    bpm=85,
    filter_resonance=0.8,
    echo_feedback_min=0.4,
    echo_feedback_max=0.9
)

# Then add fatness to individual tracks
add_sub_bass_harmonic(track_index=0, harmonic_octave=-1, harmonic_volume=0.3)
create_parallel_bass_compression(track_index=0, compression_amount=0.5)
enhance_kick_drum(track_index=1, boost_attack=True, attack_db=12)
setup_sidechain_pump(source_track=0, target_tracks=[2, 3, 4])

# Add stereo width
apply_stereo_widening(track_index=2, method="haas", width_percent=60)
apply_stereo_widening(track_index=3, method="mid_side", width_percent=80)
```

---

## 📊 **FREQUENCY REFERENCE**

### Sub-Bass (20-60Hz)
- **Effect**: Weight, power, chest thump
- **Boost**: +4 to +8dB
- **Cut**: Only if muddy or boomy
- **Best for**: Kick, sub-bass, synth bass

### Low Bass (60-150Hz)
- **Effect**: Fullness, body, warmth
- **Boost**: +3 to +6dB
- **Cut**: If muddy with other low instruments
- **Best for**: Bass, male vocals, kick tail

### Low Mids (150-400Hz)
- **Effect**: Warmth, thickness
- **Boost**: +2 to +4dB
- **Cut**: If boxy or honky
- **Best for**: Snare body, bass guitar, vocals

### Mids (400-2000Hz
