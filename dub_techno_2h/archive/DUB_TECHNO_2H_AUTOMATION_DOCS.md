# 2-HOUR DUB TECHNOPO - AUTOMATION FEATURES DOCUMENTATION

## OVERVIEW

This document describes the **full automation capabilities** implemented for the 2-hour dub techno project.

---

## AUTOMATION SCRIPT: `auto_play_2h_dub_techno.py`

### Purpose

Automates the **complete 2-hour playback** including:
- Automatic scene progression (timer-based)
- Device parameter automation
- Track volume/pan control
- Send level automation targets
- Filter automation for pads
- Progress tracking
- Graceful stopping (Ctrl+C)

---

## FEATURES IMPLEMENTED

### 1. Automatic Scene Progression

**Function**: `fire_section_clips(section_idx, section)`

**Behavior**:
- Automatically fires appropriate clips for each section
- Supports 30 sections over 2 hours (4 minutes each)
- Handles clip stopping (-1 index) and firing

**Implementation**:
```python
def fire_section_clips(section_idx, section):
    for track_idx, clip_idx in section['clips']:
        if clip_idx >= 0:
            send_command("fire_clip", {
                "track_index": track_idx,
                "clip_index": clip_idx
            })
        else:
            # Stop the track
            send_command("stop_clip", {
                "track_index": track_idx,
                "clip_index": 0
            })
```

### 2. Device Parameter Control

**Function**: `set_device_parameter(track_index, device_index, parameter_index, value)`

**Purpose**: Sets any device parameter using normalized values (0.0 to 1.0)

**Features**:
- Normalized value input (0.0 = minimum, 1.0 = maximum)
- Error handling with warnings
- Works with all device types

**Use Cases**:
- Auto Filter frequency on Synth Pads (Track 7)
- Reverb send levels
- Delay feedback amounts
- Compressor thresholds
- Any other device parameter

**Example**:
```python
# Set Auto Filter frequency to 0.50 (half-open)
set_device_parameter(7, 2, 0, 0.50)  # Track 7, Device 2 (Auto Filter), Parameter 0 (Frequency)
```

### 3. Track Volume Control

**Function**: `set_track_volume(track_index, volume_db)`

**Purpose**: Set track volume in dB with automatic normalization

**Features**:
- dB input (e.g., -6, -12, -20)
- Automatic conversion to normalized 0.0-1.0 range
- Assumed range: -70 dB to +6 dB
- Linear approximation for simplicity

**Mapping**:
```
Volume (dB) | Normalized Value
--------------|-----------------
-70 dB       | 0.00
-6 dB        | ~0.84
-12 dB       | ~0.76
-20 dB       | ~0.66
0 dB         | ~0.92
+6 dB        | 1.00
```

**Example**:
```python
set_track_volume(4, -7)   # Kick at -7 dB
set_track_volume(7, -20)  # Pads at -20 dB
```

### 4. Track Pan Control

**Function**: `set_track_pan(track_index, pan_value)`

**Purpose**: Set stereo panning

**Features**:
- Normalized range: -1.0 (left) to +1.0 (right)
- 0.0 = center
- Error handling

**Example**:
```python
set_track_pan(7, -0.2)  # Slight left pan
set_track_pan(8, 0.3)   # Slight right pan
```

### 5. Automation Point Addition

**Function**: `add_automation_point(track_index, clip_index, device_index, parameter_index, time_val, value)`

**Purpose**: Add envelope automation points to clips

**Features**:
- Time position in beats
- Normalized value (0.0-1.0)
- Linear curve type (0)
- Per-clip automation

**Example**:
```python
# Add filter automation at beat 8.0
add_automation_point(7, 0, 2, 0, 8.0, 0.50)
```

### 6. Section-Specific Automation

**Function**: `apply_section_automation(section_idx, section)`

**Purpose**: Apply all automation for a specific section

**Automated Parameters**:

#### Auto Filter (Track 7 - Synth Pads)
- **Device Index**: 2 (assumes EQ at 0, Auto Filter at 2)
- **Parameter Index**: 0 (Frequency)
- **Values**: 0.0 to 0.80 normalized
  - 0.0: Closed filter (400 Hz)
  - 0.20: Slightly open (800 Hz)
  - 0.40: Moderately open (1200-1600 Hz)
  - 0.80: Fully open (2000 Hz)

**Per-Section Values**:
| Section | Filter Freq | State |
|----------|-------------|-------|
| 0 | 0.10 | Deep intro |
| 1 | 0.15 | Subtle build |
| 2 | 0.20 | Atmosphere enters |
| 3 | 0.25 | First movement |
| ... | ... | ... |
| 10 | 0.80 | **PEAK INTENSITY** (fully open) |
| ... | ... | ... |
| 14 | 0.20 | Space (pads only) |
| 29 | 0.20 | **CLOSED** (fade out) |

#### Track Volumes
Applies volume changes per section:

| Track | Base | Variations |
|-------|-------|------------|
| 4 - Kick | -7 dB | Slight boosts during peaks (+1-2 dB) |
| 5 - Sub-bass | -5 dB | Drops during breakdowns (-3-6 dB) |
| 6 - Hi-hats | -14 dB | Muted during breakdowns |
| 7 - Pads | -20 dB | Varies with filter: louder when open, quieter when closed |
| 8 - FX | -18 dB | Muted most of time |
| 9 - Delays | -17 dB | Consistent |

#### Sends (Information Only)
- **Reverb Send levels**: Printed as targets (0.0-1.0 normalized)
  - Example: "Target sends - Reverb: 0.60, Delay: 0.35"
  - **Note**: These are informational targets - actual send adjustment requires manual configuration in Ableton

- **Delay Send levels**: Printed as targets (0.0-1.0 normalized)
  - Example: "Target sends - Reverb: 0.60, Delay: 0.35"
  - **Note**: These are informational targets - actual send adjustment requires manual configuration in Ableton

### 7. Timer-Based Progression

**Feature**: `wait_for_section_duration(section_minutes=4)`

**Behavior**:
- Waits exactly 4 minutes (240 seconds) between section changes
- Provides countdown-style output
- Ensures accurate 2-hour total duration

**Implementation**:
```python
def wait_for_section_duration(section_minutes=4):
    section_seconds = section_minutes * 60
    print(f"\n  Waiting {section_minutes} minutes ({section_seconds} seconds)...")
    time.sleep(section_seconds)
```

### 8. Progress Tracking

**Feature**: Progress bar and elapsed time

**Output Format**:
```
[========--] 0% Section 0/29 | Elapsed: 0:00
--------------------------------------------------------------------
  Section 0 - Deep Intro
  Minimal elements establish groove
--------------------------------------------------------------------
```

**Progress Updates**:
- Bar visualization (30 sections total)
- Percentage complete
- Elapsed time (HH:MM format)
- Current section name and description

### 9. Error Handling

**Features**:

#### Graceful Degradation
- **Device parameter errors**: Logged as warnings, automation continues
- **Track volume errors**: Logged as warnings, automation continues
- **Clip firing errors**: Logged as errors, but progression continues

#### User Interruption (Ctrl+C)
- **Graceful stop**: Stops automation at current section
- **Playback stop**: Sends stop command to Ableton
- **Status report**: Shows elapsed time and current section
- **Cleanup**: Closes connection properly

**Example Output**:
```
================================================================================
AUTOMATION STOPPED BY USER
================================================================================

Stopped at: 0 hours 08 minutes
Current Section: 2

[STOP] Stopping playback...
[OK] Playback stopped
```

---

## SECTION DEFINITIONS (30 Sections)

Each section includes:

```python
{
    "name": "Section X - Description",
    "description": "What's happening",
    "clips": [(track, clip), ...],  # Clips to fire
    "filter_freq": 0.XX,              # Auto Filter on Track 7
    "reverb_send": 0.XX,              # Target Reverb send (normalized)
    "delay_send": 0.XX,               # Target Delay send (normalized)
    "pad_volume": -XX,                 # Track 7 volume in dB
}
```

### Section Breakdown

#### Phase 1: Introduction (Sections 0-3)
- **0**: Deep Intro - Filter closed (0.10), minimal clips
- **1**: Subtle Build - Filter slightly open (0.15), more delays
- **2**: Atmosphere Enters - Filter opening (0.20), pads active
- **3**: First Movement - Filter more open (0.25), bass breathing

#### Phase 2: Hypnotic Groove (Sections 4-7)
- **4**: Hypnotic Lock - Filter stable (0.30), full groove
- **5**: Subtle Shift - Filter stable (0.30), bass variation
- **6**: Pad Evolution - Filter opening (0.40), chord change
- **7**: Deepening - Filter more open (0.35), more depth

#### Phase 3: First Build (Sections 8-11)
- **8**: Gathering Energy - Filter opening (0.45), hi-hats active
- **9**: More Movement - Filter opening (0.55), kick emphasis
- **10**: Peak Intensity - **Filter FULLY OPEN (0.80)**, all elements
- **11**: Holding Pattern - Filter slightly closed (0.75), sustain

#### Phase 4: Breakdown (Sections 12-15)
- **12**: Thinning Out - Filter closing (0.60), removing elements
- **13**: Just Kick and Bass - Filter closed (0.50), rhythmic core
- **14**: Space and Atmosphere - **Filter VERY CLOSED (0.20)**, just pads
- **15**: Re-emerging - Filter opening (0.30), pads return

#### Phase 5: Second Build (Sections 16-19)
- **16**: Gradual Return - Filter opening (0.40), building
- **17**: New Energy - Filter opening (0.50), more active
- **18**: Complex Layers - Filter opening (0.65), more delays
- **19**: Peak Again - **Filter FULLY OPEN (0.80)**, maximum intensity

#### Phase 6: Journey Continues (Sections 20-23)
- **20**: Deep Hypnosis - Filter stable (0.55), sustaining groove
- **21**: Minor Shift - Filter closing (0.50), soft kick
- **22**: Pad Evolution - Filter closing (0.45), atmospheric shift
- **23**: Gathering Again - Filter opening (0.55), building energy

#### Phase 7: Final Push (Sections 24-27)
- **24**: Complex Rhythms - Filter opening (0.70), kick syncopation
- **25**: Maximum Movement - **Filter FULLY OPEN (0.80)**, all elements
- **26**: Holding Peak - Filter slightly closed (0.75), sustaining
- **27**: Beginning Release - Filter closing (0.60), thinning out

#### Phase 8: Wind Down (Sections 28-29)
- **28**: Returning to Simplicity - Filter closing (0.45), stripping back
- **29**: Fading Out - **Filter FULLY CLOSED (0.20)**, final breakdown

---

## USAGE INSTRUCTIONS

### Running the Full Automation

**Command**:
```bash
python auto_play_2h_dub_techno.py
```

**What Happens**:
1. **Starts playback** - Sends start command to Ableton
2. **Shows header** - Displays total duration and section count
3. **Begins loop**:
   - Fires clips for Section 0
   - Applies automation for Section 0
   - Waits 4 minutes
   - Fires clips for Section 1
   - Applies automation for Section 1
   - Waits 4 minutes
   - (continues through all 30 sections...)
4. **Completes** - Shows completion message after 2 hours
5. **Closes connection** - Properly terminates socket connection

**Stopping Automation**:
- Press **Ctrl+C** at any time
- Automation stops gracefully
- Ableton playback stops
- Status report shows elapsed time

### Prerequisites

**Before running automation**:

1. **Complete setup scripts** (must run first):
   ```bash
   python create_2h_dub_techno.py      # Creates tracks and clips
   python load_instruments_and_effects.py  # Loads instruments and effects
   ```

2. **Verify session state**:
   - 12 tracks total
   - 48 MIDI clips created
   - Instruments loaded on tracks 4-8
   - Effects added
   - Send tracks 10-11 created

3. **Configure manually** (recommended before automation):
   - Load instrument presets on tracks 4-8
   - Set up send routing in Ableton (tracks 4-9 send to 10-11)
   - Set initial mix levels
   - Configure reverb and delay effects

### Output During Automation

Example of what you'll see:

```
================================================================================
2-HOUR DUB TECHNOPO - AUTOMATED PLAYBACK
================================================================================
Total Duration: 120 minutes (2 hours)
Total Sections: 30
Section Duration: 4 minutes each
================================================================================

[START] Starting playback...
[OK] Playback started

================================================================================
BEGINNING AUTOMATED SECTION PROGRESSION
================================================================================

Press Ctrl+C to stop automation


[------------------------------] 0% Section 0/29 | Elapsed: 0:00
--------------------------------------------------------------------
  Section 0 - Deep Intro
  Minimal elements establish groove
--------------------------------------------------------------------

  Applying automation for Section 0 - Deep Intro...
    [OK] Auto Filter: 0.10
    [OK] Track 4 volume: -7 dB
    [OK] Track 5 volume: -5 dB
    [OK] Track 6 volume: -14 dB
    [OK] Track 7 volume: -20 dB
    [OK] Track 8 volume: -18 dB
    [OK] Track 9 volume: -17 dB
    [INFO] Target sends - Reverb: 0.40, Delay: 0.25

  Firing clips for Section 0 - Deep Intro...
    [OK] Track 4, Clip 0
    [OK] Track 5, Clip 0
    [OK] Track 6, Clip 2
    [STOP] Track 7
    [OK] Track 7, Clip 4
    [STOP] Track 8
    [OK] Track 8, Clip 3
    [OK] Track 9, Clip 2

  Waiting 4 minutes (240 seconds)...

[=====------] 3% Section 1/29 | Elapsed: 0:04
--------------------------------------------------------------------
  Section 1 - Subtle Build
  Adding slight variations, more delays
--------------------------------------------------------------------

  Applying automation for Section 1 - Subtle Build...
    [OK] Auto Filter: 0.15
    [OK] Track 4 volume: -7 dB
    ...

  Firing clips for Section 1 - Subtle Build...
    ...
```

---

## AUTOMATION CAPABILITIES SUMMARY

| Feature | Status | Description |
|---------|--------|-------------|
| Automatic scene progression | ✅ Implemented | Timer-based, 30 sections over 2 hours |
| Device parameter control | ✅ Implemented | Normalized values (0.0-1.0) |
| Track volume automation | ✅ Implemented | dB input, automatic normalization |
| Track pan control | ✅ Implemented | Stereo panning (-1.0 to +1.0) |
| Clip envelope automation | ✅ Implemented | Per-point automation with time values |
| Filter automation (pads) | ✅ Implemented | Auto Filter frequency per section |
| Send level targets | ✅ Implemented | Informational targets for manual setup |
| Progress tracking | ✅ Implemented | Visual progress bar and elapsed time |
| Graceful stopping | ✅ Implemented | Ctrl+C interrupt handling |
| Error recovery | ✅ Implemented | Warnings for failures, continues execution |

---

## MANUAL SETUP STILL REQUIRED

While automation handles progression and parameter changes, **manual setup is still needed**:

### 1. Instrument Presets

**Tracks 4-8** need instrument presets:
- **Track 4 (Kick)**: Punchy kick sound in Operator
- **Track 5 (Sub-bass)**: Deep sub sound in Tension
- **Track 6 (Hi-hats)**: Load hi-hat samples in Drum Rack
- **Track 7 (Synth Pads)**: Atmospheric pad preset in Wavetable
- **Track 8 (FX)**: Load FX samples in Simpler

### 2. Send Routing (in Ableton)

**Required**: Manual setup in Ableton Session View

**Tracks 4-9** must send to:
- **Track 10 (Reverb Send)** - Send A
- **Track 11 (Delay Send)** - Send B

**Suggested Levels**:
| Track | Reverb Send | Delay Send |
|-------|-------------|------------|
| 4 - Kick | 0% | 0% |
| 5 - Sub-bass | 0% | 5-10% |
| 6 - Hi-hats | 20-30% | 25-35% |
| 7 - Pads | 40-50% | 20-30% |
| 8 - FX | 60-70% | 70-80% |
| 9 - Delays | 80-90% | 100% |

### 3. Initial Mix Levels

**Tracks 4-9** need initial volume levels (automation adjusts from these):
| Track | Target dB |
|-------|-----------|
| 4 - Kick | -6 to -8 dB |
| 5 - Sub-bass | -3 to -6 dB |
| 6 - Hi-hats | -12 to -15 dB |
| 7 - Pads | -18 to -24 dB |
| 8 - FX | -15 to -20 dB |
| 9 - Delays | -15 to -18 dB |

### 4. Effect Configuration

**Track 10 (Reverb Send)** - Hybrid Reverb:
- Size: Large (70-90%)
- Decay Time: 3-5 seconds
- Volume: -15 dB

**Track 11 (Delay Send)** - Simple Delay:
- Time: 1/4 or 1/8 notes (dub delay)
- Feedback: 35-50%
- Dry/Wet: 30-40% wet
- Volume: -12 dB

---

## LIMITATIONS AND NOTES

### What Automation Can Do

✅ **Automatic clip firing** - Progresses through 30 sections automatically
✅ **Filter automation** - Auto Filter on Track 7 changes per section
✅ **Track volume automation** - Adjusts volume per section
✅ **Progress tracking** - Shows progress and elapsed time
✅ **Graceful stopping** - Ctrl+C to stop anytime
✅ **Error recovery** - Continues despite parameter errors

### What Automation Cannot Do (Yet)

❌ **Send level automation** - Only prints targets, must set manually in Ableton
  - **Reason**: Send routing requires Ableton UI interaction or more advanced API

❌ **Device preset loading** - Cannot load presets programmatically
  - **Reason**: Preset selection is complex, not exposed via basic MCP commands

❌ **Automation envelope creation** - Can add points, but envelope automation needs manual refinement
  - **Reason**: Complex envelope shapes and transitions require Ableton UI

❌ **Continuous parameter modulation** - Can set discrete values, not continuous LFO modulation
  - **Reason**: LFOs and continuous modulation are device-specific

---

## ADVANCED AUTOMATION (Future Enhancements)

### Potential Improvements

1. **Clip Automation Envelope Creation**
   - Generate complete automation envelopes in one pass
   - Add multiple points per parameter per section
   - Create smooth curves between points

2. **Send Level Control via Device Parameters**
   - If send devices expose parameter controls, automate them directly
   - Eliminates manual setup requirement

3. **Preset Management System**
   - Store preset states for each section
   - Save/restore preset combinations
   - Enable instant section switching

4. **Real-Time Performance Mode**
   - Manual trigger of sections via keypress
   - Live performance adjustments
   - On-the-fly parameter tweaks

5. **Arrangement View Export**
   - Automatically arrange all clips in timeline
   - Create complete song structure
   - Enable linear playback without automation

---

## FILES CREATED FOR AUTOMATION

| File | Purpose | Lines |
|------|----------|-------|
| `auto_play_2h_dub_techno.py` | Full automation script | ~580 |
| `DUB_TECHNO_2H_AUTOMATION_DOCS.md` | This documentation | ~600 |

---

## CONCLUSION

The automation system provides **comprehensive control** over the 2-hour dub techno track:

### ✅ Fully Automated
- Scene progression (30 sections, 4 minutes each)
- Filter automation (Synth Pads)
- Track volume changes
- Progress tracking

### ⚙️ Partially Automated
- Device parameter control (available but limited to discrete changes)
- Send level targets (informational only, requires manual setup)

### 🔧 Manual Setup Required
- Instrument presets on tracks 4-8
- Send routing in Ableton UI
- Initial mix levels
- Effect configuration (reverb, delay settings)

---

**The automation script is ready to run!**

Just complete the manual setup steps, then run:
```bash
python auto_play_2h_dub_techno.py
```

And enjoy your 2-hour automated dub techno journey! 🎵

---

*Last Updated: January 7, 2026*
