# 10-Minute Dub Reggae Beat

A complete dub reggae beat generator and automation system using the Ableton MCP server.

## Overview

This project creates a **10-minute dub reggae beat** with authentic reggae patterns, dub production techniques, and automated arrangement evolution.

**Key Features:**
- **Tempo:** 75 BPM (classic dub feel)
- **Duration:** 10 minutes
- **Tracks:** 8 instrument tracks + 2 send tracks
- **Sections:** 10 sections × 1 minute each
- **Instruments:** Drums (One Drop), Dub Bass, Guitar Chop, Organ Bubble, FX, Dub Delays
- **Effects:** Reverb sends, Delay sends, Filter automation

## What's Included

### 1. `create_10min_dub_reggae.py`
Main setup script that creates:
- **10 tracks** (8 MIDI + 2 audio send)
- **48 clips** (4-8 clips per track)
- **10 arrangement sections**
- **Base track volumes**
- **Tempo (75 BPM)**

### 2. `play_10min_dub_reggae.py`
Automation playback script that:
- Starts playback
- Loops through 10 sections
- Fires clips for each section
- Logs automation targets
- Displays progress
- Handles graceful shutdown

## Track Structure

| Track | Purpose | Clip Count |
|-------|---------|------------|
| **Kick** | One Drop pattern (beat 3) | 4 |
| **Snare** | Beats 2 & 4 | 4 |
| **Hi-hats** | Offbeat pattern | 4 |
| **Dub Bass** | Root drones, walking, syncopated | 8 |
| **Guitar Chop** | Offbeat chord stabs | 4 |
| **Organ Bubble** | Shuffle/stab patterns | 4 |
| **FX** | Percussion hits, impacts | 4 |
| **Dub Delays** | Echo patterns | 3 |
| **Reverb Send** | Return track for reverb | - |
| **Delay Send** | Return track for delay | - |

## Arrangement Structure

```
Section 0: Intro (0:00-1:00)
  - Minimal: Bass + Drums only
  - Filter: Closed (0.2)

Section 1: Build (1:00-2:00)
  - Add: Guitar chop
  - Filter: Opening (0.3)

Section 2: Add Organ (2:00-3:00)
  - Add: Organ bubble
  - Filter: Opening (0.4)

Section 3: Peak 1 (3:00-4:00)
  - Full groove with all elements
  - Filter: Open (0.7)

Section 4: Breakdown (4:00-5:00)
  - Strip down to bass + drums
  - Filter: Closed (0.25)

Section 5: Rebuild (5:00-6:00)
  - Gradually bring elements back
  - Filter: Opening (0.4)

Section 6: Peak 2 (6:00-7:00)
  - Intense, all effects active
  - Filter: Wide open (0.8)

Section 7: Variation (7:00-8:00)
  - Change key to F minor
  - Filter: Mid (0.5)

Section 8: Peak 3 (8:00-9:00)
  - Maximum intensity
  - Filter: Wide open (0.85)

Section 9: Wind Down (9:00-10:00)
  - Gradual fade to minimal
  - Filter: Closed (0.2)
```

## Installation & Setup

### Prerequisites

1. **Ableton Live 11+** installed
2. **AbletonMCP Remote Script** loaded in Ableton
   - Path: `AbletonMCP_Remote_Script/` → Copy to Ableton MIDI Remote Scripts folder
3. **MCP Server** running:
   ```bash
   cd MCP_Server
   python server.py
   ```
4. **Ableton Live** open with Remote Script active (check "C:Users" in Live's Preferences → Link MIDI)

### Usage

#### Step 1: Create Tracks and Clips

```bash
python create_10min_dub_reggae.py
```

**What happens:**
- Creates 10 tracks
- Creates 48 clips
- Sets tempo to 75 BPM
- Sets base volumes
- Prints confirmation

**Manual setup required:**
1. Load instruments on each track:
   - **Kick**: Drum Rack (kick sample)
   - **Snare**: Drum Rack (snare sample)
   - **Hi-hats**: Drum Rack (hi-hat samples)
   - **Dub Bass**: Tension or Operator (sub-heavy)
   - **Guitar Chop**: Instrument Rack (guitar/organ)
   - **Organ Bubble**: Organ or Electric Piano
   - **FX**: Simpler (percussion samples)
   - **Dub Delays**: Utility (for send routing)

2. Load effects on send tracks:
   - **Reverb Send**: Reverb (Large Hall, 2-3s decay)
   - **Delay Send**: Simple Delay or Ping Pong Delay (1/4 or 1/8 note, 35-50% feedback)

3. Set up send routing:
   - All tracks → Send A → Delay Send (20-40%)
   - All tracks → Send B → Reverb Send (15-35%)

4. Optional: Add Auto Filter to synth tracks for automation

#### Step 2: Run Automation

```bash
python play_10min_dub_reggae.py
```

**What happens:**
- Starts playback
- Loops through 10 sections
- Fires clips for each section
- Logs automation targets (filter, reverb, delay)
- Displays progress
- Stops after 10 minutes

**Manual automation required:**
- Adjust filter frequency (0.0-1.0) on synth tracks during sections
- Adjust send levels (delay/reverb) during sections
- See console output for target values per section

## Pattern Details

### Drum Patterns

**Kick (One Drop):**
- Beat 3 only (classic reggae "one drop" pattern)
- Variations: Heavy, Light, Muted

**Snare:**
- Beats 2 & 4
- Variations: Basic, Accent, Muted, Ghost notes

**Hi-hats:**
- Offbeats (beats 1&, 2&, 3&, 4&)
- Variations: Basic, Active, Sparse, Muted

### Bass Patterns

**Root Drones:**
- C2 (36), F2 (41), D2 (38), Bb1 (34)
- Long held notes (4 beats)
- Dub bass foundation

**Melodic Patterns:**
- Walking: Root → 3rd → 5th → 7th
- Syncopated: Offbeat hits, octave drops
- One Drop: Kick-synced pattern

**Intervals:**
- Root-5th: C to G (36 to 43)
- Root-3rd: C to Eb (36 to 39)
- Root-Flat 7: C to Bb (36 to 34)

### Guitar Chop Patterns

**Offbeat Chord Stabs:**
- On "and" of each beat (1&, 2&, 3&, 4&)
- Short duration (0.15 beats)
- Triads: C Major (48, 51, 55), F Major (51, 55, 58), Fm (43, 48, 51)

### Organ Bubble Patterns

**Shuffle Pattern:**
- Double-time upper register
- C major triad alternating (60, 63)
- 8th note rhythm

**Stab Pattern:**
- Offbeat chords (1&, 2&, 3&, 4&)
- Full bar chords

**Low Pattern:**
- Lower register chord hits on beats 2 & 4
- Sparse, fills space

### FX Patterns

- Sub Hits (low-frequency impacts)
- Cymbal crashes (transitional)
- Noise builds (rising texture)
- Muted (silence)

### Dub Delay Patterns

- Echo shots (delayed hits)
- Active delays (multiple echoes)
- Muted (silence)

## Dub Production Techniques

### Delay Automation

**Setup:**
- Send tracks → Delay Return
- Delay: Simple Delay / Ping Pong Delay
- Time: 0.5-0.8 seconds
- Feedback: 35-50%
- Filter: Low-pass 2-4 kHz on return

**Automation Pattern:**
- Gradual increase during builds
- Decrease during breakdowns
- "Delay shots": Single snare/hit with echo boost

### Reverb Automation

**Setup:**
- Send tracks → Reverb Return
- Reverb: Medium room, 1.5-2.5s decay
- Pre-delay: 20-50ms

**Automation Pattern:**
- NOT constant
- "Room shots": Burst on single hits (every 4-8 bars)
- More during breakdowns, less during peaks

### Filter Automation

**Setup:**
- Auto Filter on synth tracks
- Low-pass cutoff: 200 Hz - 10 kHz

**Automation Pattern:**
- Intro: Closed (muffled)
- Build: Opening gradually
- Peak: Wide open (bright)
- Breakdown: Closed (distant)
- Rebuild: Opening again

### Creative Muting

**Pattern:**
- Alternate muting every 8-16 bars
- Sudden drops on beat (create impact)
- Gradual fade-ins (0% → 100% over 2-4 bars)

## Automation Targets

Per section, the script logs these automation targets:

| Section | Filter | Reverb Send | Delay Send |
|---------|---------|--------------|-------------|
| Intro | 0.20 | 0.30 | 0.20 |
| Build | 0.30 | 0.40 | 0.25 |
| Add Organ | 0.40 | 0.50 | 0.35 |
| Peak 1 | 0.70 | 0.60 | 0.50 |
| Breakdown | 0.25 | 0.60 | 0.20 |
| Rebuild | 0.40 | 0.40 | 0.30 |
| Peak 2 | 0.80 | 0.65 | 0.55 |
| Variation | 0.50 | 0.50 | 0.40 |
| Peak 3 | 0.85 | 0.70 | 0.60 |
| Wind Down | 0.20 | 0.80 | 0.30 |

## Troubleshooting

### "Track not found" error
- Run `create_10min_dub_reggae.py` first
- Check Ableton Remote Script is loaded
- Verify MCP Server is running on port 9877

### No sound
- Load instruments on each track
- Check track volumes (script sets base levels)
- Verify sends are routed to return tracks
- Check instrument plugin presets

### Automation not working
- Script logs target values only
- Manual automation required in Ableton
- Use console output as guide for target values
- Consider using follow actions for clip progression

### Clips not firing
- Check track indices match clip slots
- Verify clips were created (check Ableton session view)
- Test manual clip launch first

### Timing issues
- Verify tempo is 75 BPM (script sets this)
- Check Ableton's global quantize settings
- Restart playback if timing drifts

## Customization

### Change Tempo
Edit `create_10min_dub_reggae.py`:
```python
send_command("set_tempo", {"tempo": 75.0})  # Change to desired BPM
```

### Change Duration
Edit `play_10min_dub_reggae.py`:
```python
# In main loop, change wait time
time.sleep(60)  # Change from 60 to desired seconds per section
```

### Add New Patterns
1. Add new clip definitions in `create_10min_dub_reggae.py`
2. Create the clip with `send_command("create_clip", ...)`
3. Add notes with `send_command("add_notes_to_clip", ...)`
4. Reference new clips in sections list

### Modify Sections
Edit `sections` list in both scripts:
- Change clip indices
- Modify filter/reverb/delay targets
- Add/remove sections as needed

## Advanced Features

### Clip Follow Actions
Automate clip progression without script:
```python
# In create_10min_dub_reggae.py
send_command("set_clip_follow_action", {
    "track_index": track_idx,
    "clip_index": clip_idx,
    "action_slot": 0,
    "action_type": 3,  # Other (play specific clip)
    "trigger_time": 4.0,
    "clip_index_target": next_clip_idx
})
```

### Parameter Automation
Automate filter, send levels programmatically:
```python
# Get device parameters
params = send_command("get_device_parameters", {
    "track_index": track_idx,
    "device_index": 0
})

# Set parameter
send_command("set_device_parameter", {
    "track_index": track_idx,
    "device_index": 0,
    "parameter_index": 0,
    "value": 0.75
})
```

### Envelope Automation
Create automation envelopes in clips:
```python
# Add automation point
send_command("add_automation_point", {
    "track_index": track_idx,
    "clip_index": clip_idx,
    "device_index": 0,
    "parameter_index": 0,
    "time": 0.0,
    "value": 0.5
})
```

## Musical Theory

### Key: C Minor
- C (root), Eb (minor 3rd), F (perfect 4th), G (perfect 5th), Bb (minor 7th)
- Common in reggae/dub for minor, melancholic feel

### One Drop Rhythm
- Kick on beat 3 only (skips beat 1)
- Creates space and anticipation
- Classic reggae drum pattern

### Offbeat Emphasis
- Guitar/organ on "and" of beats
- Creates syncopated, propulsive feel
- Fundamental to reggae groove

### Sub-Bass Dominance
- Bass sits high in mix relative to other instruments
- Carries primary melodic/rhythmic content
- Essential to dub aesthetic

## References & Inspiration

**Classic Dub Albums:**
- King Tubby - "King Tubby Meets the Rockers Uptown"
- Lee "Scratch" Perry - "Super Ape"
- Scientist - "Scientist Rids the World of the Evil Curse"
- Augustus Pablo - "King Tubby Meets Rockers Uptown"

**Production Techniques:**
- Real-time mixing as performance (mutes, sends, filters)
- Extensive use of delay and reverb
- Creative EQ filtering and frequency manipulation
- Space and atmosphere over complexity

## License

This project is part of the ableton-mcp-extended repository.

## Support

For issues or questions:
1. Check Ableton Remote Script is loaded
2. Verify MCP Server is running
3. Consult AGENTS.md for detailed guidelines
4. Review MCP_ENHANCED_AUTOMATION_GUIDE.md

---

**Created by Sisyphus (AI Agent)**
**Date: 2025-01-08**
**Version: 1.0**
