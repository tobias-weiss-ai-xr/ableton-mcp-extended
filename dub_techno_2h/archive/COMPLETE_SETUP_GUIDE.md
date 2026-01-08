# Complete 2-Hour Dub Techno Automation Guide

## Overview

This guide walks you through the complete setup and automation of a 2-hour dub techno track using the Ableton MCP system.

**Total Duration**: 2 hours (120 minutes)
**Structure**: 30 sections × 4 minutes each
**Tempo**: 126 BPM
**Tracks**: 8 total (6 main + 2 sends)

---

## Quick Start (10 minutes automated setup + 10-15 minutes manual config)

### Step 1: Automated Setup (10 minutes)

Run these scripts in order:

```bash
cd dub_techno_2h

# 1. Create tracks and clips (4-5 minutes)
python create_2h_dub_techno.py

# 2. Load instruments and effects (5 minutes)
python load_instruments_and_effects.py
```

**What gets created:**
- ✅ 6 main tracks (Kick, Sub-bass, Hi-hats, Synth Pads, FX, Dub Delays)
- ✅ 48 MIDI clips (8 per track)
- ✅ 2 send tracks (Reverb Send, Delay Send)
- ✅ Instruments loaded on each track
- ✅ Effects (EQ, Compressor, Reverb, Delay, Auto Filter, Utility)

### Step 2: Manual Configuration (10-15 minutes)

**CRITICAL**: These steps must be done manually in Ableton Live - they cannot be automated via API.

#### 2.1 Configure Instrument Presets (5 minutes)

For each track, open the device and select/load the preset:

| Track | Instrument | Preset/Type | Action |
|-------|------------|---------------|---------|
| 0 - Kick | Operator | Kick - Punchy | Create punchy 4/4 kick |
| 1 - Sub-bass | Tension | Sub Bass - Deep | Design deep sub drone |
| 2 - Hi-hats | Drum Rack | Basic Kit | Load hi-hat samples |
| 3 - Synth Pads | Wavetable | Atmospheric | Choose pad preset |
| 4 - FX | Simpler | FX - One Shot | Load sweep/impact samples |
| 5 - Dub Delays | N/A | N/A | Send track only |

**How to:**
- Double-click the instrument device to open it
- Browse to the preset in Ableton's browser
- Drag preset onto device
- Press playback to test sound

#### 2.2 Configure Send Routing (5-10 minutes - **MOST IMPORTANT**)

This is the key to the dub techno sound. Send each main track to Reverb and Delay sends.

**For each track 0-5:**

1. Click the track to select it
2. Click the **Sends** button (below the clip matrix, above track mixer)
3. Click the **Audio To** dropdown menu (appears after clicking Sends)
4. Select **6 - Reverb Send**
5. Adjust the Reverb send level knob to the target value below
6. Click the **+** button next to the sends dropdown
7. Select **7 - Delay Send**
8. Adjust the Delay send level knob to the target value below

**Send Level Targets:**

| Track | To Reverb Send | To Delay Send | Purpose |
|-------|----------------|----------------|---------|
| 0 - Kick | 0% (off) | 0% (off) | Clean punch |
| 1 - Sub-bass | 10% | 10% | Subtle depth |
| 2 - Hi-hats | 30% | 30% | Space and shimmer |
| 3 - Synth Pads | 50% | 50% | Atmospheric depth |
| 4 - FX | 70% | 70% | Max effect |
| 5 - Dub Delays | 100% | 100% | Echo tail destination |

**Visual Guide:**
```
Track 5 (Dub Delays) Mixer:
┌─────────────────────────────────────────────────────┐
│ Sends button clicked?  [YES]                   │
│                                             │
│ Sends:                                      │
│ ┌─────────────┐   ┌─────────────┐         │
│ │ Reverb     │   │ Delay      │         │
│ │ 100% ██████│   │ 100% ██████│         │
│ └─────────────┘   └─────────────┘         │
│                                             │
│ [+ button to add more sends]                  │
└─────────────────────────────────────────────────────┘
```

#### 2.3 Configure Send Effects (3-5 minutes)

**Track 6 - Reverb Send:**
- Double-click Hybrid Reverb device
- Set **Size**: Large (50-80%)
- Set **Decay**: Long (3-5 seconds)
- Set **High Cut**: ~4000 Hz
- Set **Wet/Dry**: 100%

**Track 7 - Delay Send:**
- Double-click Simple Delay device
- Set **Sync**: On
- Set **Time**: 1/4 or 1/8 note
- Set **Feedback**: 40-60%
- Set **Wet/Dry**: 100%

#### 2.4 Configure Track Volumes (2-3 minutes)

These have been preset by the script, but verify/adjust if needed:

| Track | Volume (normalized) | dB Level | Action |
|-------|-------------------|-----------|---------|
| 0 - Kick | 0.75 | -6 dB | Reference level |
| 1 - Sub-bass | 0.60 | -3 dB | Slightly below kick |
| 2 - Hi-hats | 0.30 | -12 dB | Subtle |
| 3 - Synth Pads | 0.15 | -18 dB | Background |
| 4 - FX | 0.20 | -15 dB | Occasional |
| 5 - Dub Delays | 0.25 | -12 dB | Echo |
| 6 - Reverb Send | 0.25 | -12 dB | Effects |
| 7 - Delay Send | 0.20 | -14 dB | Effects |

**How to adjust:**
- Click track to select it
- Drag the volume fader up/down
- Watch the dB meter or use the mixer section

#### 2.5 Save Project

Press **Ctrl+S** (Windows) or **Cmd+S** (Mac) to save the Ableton project.

---

## Step 3: Enable Recording (2 minutes)

Choose one of these methods:

### Option A: Master Recording (Manual Start)

1. Press **Shift+R** to arm the Master track for recording
2. Master track header will glow red
3. Press the **Record** button (or press **R** key)
4. Recording starts
5. After 2 hours, stop recording
6. Export the recorded audio from Master track

### Option B: Live Export (RECOMMENDED)

1. Go to **File** → **Export Audio/Video**
2. Set the following:
   - **Source**: Master
   - **Format**: WAV (best quality) or MP3
   - **Bit Depth**: 24-bit (WAV only)
   - **Sample Rate**: 44100 Hz
   - **Duration**: 2:00:00 (2 hours exactly)
3. Click **Export**
4. Ableton will export while the automation script runs

**File will be named**: `dubking.mp3` (or .wav)
**Location**: Ableton Exports folder (usually Documents/.../Ableton/Exports)

---

## Step 4: Run 2-Hour Automation (2 hours - fully automated)

Once manual configuration is complete and recording is enabled:

```bash
cd dub_techno_2h

# Start the 2-hour automation
python auto_play_2h_dub_techno.py
```

**What happens during automation:**
- ✅ Automatic clip firing every 4 minutes
- ✅ Progress tracking with visual bar: `[======----] 15%`
- ✅ Time display: `00:16 Section 4 - Hypnotic State`
- ✅ 30 sections with varying clip combinations
- ✅ No manual intervention needed
- ✅ Graceful stop on Ctrl+C

**Console Output Example:**
```
FULLY AUTOMATED 2-HOUR DUB TECHNOPO PLAYBACK
============================================================================

[00:00] Section 0 - Deep Intro
  [OK] Playback started

[======---] 15%
[00:16] Section 4 - Hypnotic State
  Description: Full groove engaged
  [OK] Clips fired

[============] 50%
[00:56] Section 14 - Floating
  Description: Hypnotic minimal state
  [OK] Clips fired

[========================] 100%
============================================================================
2-HOUR PLAYBACK COMPLETE!
============================================================================
```

---

## Section Timeline (30 sections × 4 minutes)

| Phase | Sections | Time | Energy | Description |
|-------|-----------|-------|---------|-------------|
| **1: Introduction** | 0-3 | 0:00-0:16 | Minimal | Establish groove, dark atmosphere |
| **2: Hypnotic** | 4-7 | 0:16-0:32 | Groove | Full groove, subtle evolution |
| **3: First Build** | 8-11 | 0:32-0:48 | Building | Increasing energy to first peak |
| **4: Breakdown** | 12-15 | 0:48-1:04 | Space | Removing elements, atmospheric |
| **5: Second Build** | 16-19 | 1:04-1:20 | Building | Energy returns after breakdown |
| **6: Journey** | 20-23 | 1:20-1:36 | Hypnosis | Sustaining groove, subtle changes |
| **7: Final Push** | 24-27 | 1:36-1:52 | Peak | Maximum movement, complex layers |
| **8: Wind Down** | 28-29 | 1:52-2:00 | Fading | Stripping back, fading out |

---

## Troubleshooting

### "Clips don't fire"
- Verify all 48 clips were created (create_2h_dub_techno.py)
- Check that tracks 0-5 exist and have clip slots
- Re-run create_2h_dub_techno.py if needed

### "No audible changes during automation"
- Verify send routing is configured (MOST COMMON ISSUE)
- Check that volume faders are not muted
- Verify instruments have loaded presets
- Watch the Ableton mixer to see clip slots firing

### "Script won't start / Connection error"
- Ensure Ableton Live is running
- Verify AbletonMCP Remote Script is loaded (Preferences → Link/MIDI → Control Surface)
- Check that the Remote Script is in the correct folder
- Restart Ableton if needed

### "Automation script crashes"
- Check for error messages in console
- Verify all commands are supported by Remote Script
- Try running scripts individually first
- Restart Ableton and the MCP server

---

## File Summary

All scripts are in the `dub_techno_2h/` folder:

| File | Purpose | Duration | Automation Level |
|------|----------|-----------|------------------|
| `create_2h_dub_techno.py` | Create tracks and clips | 4-5 min | ✅ Fully automated |
| `load_instruments_and_effects.py` | Load instruments and effects | 5 min | ✅ Fully automated |
| `auto_play_2h_dub_techno.py` | Run 2-hour playback | 2 hours | ✅ Fully automated |

**Total Automated Work**: ~9 minutes
**Total Manual Work**: 10-15 minutes
**Total Time**: ~2 hours 24 minutes

---

## After Completion

1. **Stop Recording**
   - If using Master Recording: Press Stop or Space bar
   - If using Export: Export completes automatically

2. **Verify File**
   - Check `Ableton Exports` folder for `dubking.mp3` (or .wav)
   - Expected size: ~400-500 MB for WAV, ~50-100 MB for MP3

3. **Listen Back**
   - Play the exported file
   - Verify smooth transitions between sections
   - Check for any glitches or dropouts

4. **Share/Use**
   - Upload to streaming platforms
   - Use for DJ sets
   - Listen for meditation/focus
   - Create variations/mixes

---

## What's Automated vs Manual

### ✅ Fully Automated

- **Track Creation**: Creates all 8 tracks with correct names
- **Clip Creation**: Generates 48 MIDI clips (8 per track)
- **Tempo Setting**: Sets to 126 BPM
- **Instrument Loading**: Loads devices via Ableton browser
- **Effect Loading**: Loads reverb, delay, EQ, compressor
- **Playback Automation**: Fires clips on 4-minute intervals
- **Progress Tracking**: Shows visual progress bar and time
- **Volume Levels**: Sets initial track volumes

### ⚙️ Partially Automated

- **Preset Selection**: Devices load but presets must be chosen manually
- **Volume Adjustments**: Initial values set but may need manual fine-tuning

### ❌ Manual Only (Not possible via API)

- **Send Routing**: Must create sends in Ableton UI (critical for dub sound)
- **Preset Browsing**: Cannot navigate Ableton preset browser programmatically
- **Effect Configuration**: Reverb/delay parameters set manually
- **Recording**: Enable recording via Ableton UI
- **Project Saving**: Ctrl+S to save changes

---

## Tips for Best Results

1. **Send Routing is Key**: This is the most important manual step. Take your time to get it right.

2. **Test Before Automation**: Play through a few sections manually to verify sound before starting the full 2-hour run.

3. **Monitor CPU**: Watch Ableton's CPU meter during automation. If it gets too high, reduce plugin count or increase latency.

4. **Save Often**: Press Ctrl+S after manual configuration to ensure all changes are saved.

5. **Headphones vs Speakers**: Use headphones for detailed monitoring during setup, speakers for final listening.

6. **Volume Levels**: Start with the preset volumes and adjust gradually. The bass should be felt but not overwhelming.

---

## Support

For issues or questions:

1. Check the console output for error messages
2. Review this troubleshooting section
3. Verify all three scripts ran successfully
4. Confirm Ableton Remote Script is loaded
5. Check Ableton's Log (Help → View Error Log)

---

**Enjoy your 2-hour dub techno journey!** 🎵

Remember: The beauty of dub techno is in the subtle evolution and hypnotic repetition. Let the music breathe and evolve over time.
