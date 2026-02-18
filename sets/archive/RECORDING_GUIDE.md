# 2-HOUR DUB TECHNOPO - RECORDING GUIDE

## Overview

Your 2-hour dub techno project is ready! This guide explains how to record it to `dubking.mp3`.

## What's Been Created

✅ **6 MIDI tracks** (indices 0-5):
   - Track 0: Kick (8 clips)
   - Track 1: Sub-bass (8 clips)
   - Track 2: Hi-hats (8 clips)
   - Track 3: Synth Pads (8 clips)
   - Track 4: FX (8 clips)
   - Track 5: Dub Delays (8 clips)

✅ **48 MIDI clips** total (8 per track)
✅ **30 sections** defined (4 minutes each)
✅ **Tempo set to 126 BPM**
✅ **Automation script ready** (plays all 30 sections over 2 hours)

## Current Status

⚠️ **Tracks are created with MIDI data, but instruments need to be configured in Ableton Live**

The automation scripts have loaded the instrument devices onto the tracks, but you'll need to:

1. **Configure instrument presets** in Ableton Live UI
2. **Set up send routing** for reverb and delay effects
3. **Adjust mix levels** for proper balance
4. **Enable recording** on the Master track
5. **Run the automation script** while recording

---

## STEP 1: Configure Instruments in Ableton

Open your Ableton Live session. You should see 6 new tracks (plus any existing ones).

### Track 0: Kick
- Device: Operator (loaded)
- **Action**: Double-click Operator to open it
- Create a punchy dub kick:
  - Oscillator A: Sine wave
  - Frequency: C2 (MIDI note 36)
  - Envelope:
    - Attack: 0.010 ms (very fast)
    - Decay: 0.150 ms (short)
    - Sustain: 0.0
    - Release: 0.100 ms (short)
  - Filter: Low-pass, frequency around 200-300 Hz
- Test by firing Clip 0 - should hear 4/4 kick pattern

### Track 1: Sub-bass
- Device: Tension (loaded)
- **Action**: Configure deep sub sound:
  - Oscillator: Sine wave
  - Pitch: C2 (36)
  - Envelope: Long attack, long decay for drone
  - Filter: Low-pass, very low frequency (~80-100 Hz)
- Test by firing Clip 0 - should hear continuous bass drone

### Track 2: Hi-hats
- Device: Drum Rack (loaded)
- **Action**: Load hi-hat samples:
  - Double-click Drum Rack
  - Find/Load closed hi-hat samples (MIDI note 76 = C6)
  - Load open hi-hat samples (MIDI note 77 = C#6)
- Test by firing Clip 0 - should hear offbeat hi-hats

### Track 3: Synth Pads
- Device: Wavetable + Auto Filter (loaded)
- **Action**: Choose atmospheric pad preset:
  - Double-click Wavetable
  - Browse presets → "Pads" or "Atmospheric"
  - Select a dark, minimal pad sound
  - Auto Filter: Low-pass, modulate envelope for evolution
- Test by firing Clip 0 - should hear sustained Cm chord

### Track 4: FX
- Device: Simpler (loaded)
- **Action**: Load FX samples:
  - Double-click Simpler
  - Load sample: noise sweep, impact, reverse cymbal, sub drop
  - Set to one-shot mode
- Test by firing Clip 1 (Impact) - should hear a hit

### Track 5: Dub Delays
- Device: Utility (loaded)
- **Action**: This is a send track
  - Leave Utility as is (for gain control)
  - Configure send routing (see Step 2)

---

## STEP 2: Configure Send Routing (Critical!)

This is essential for dub techno's signature reverb and delay atmosphere.

### Create Reverb and Delay Send Tracks

If you ran `load_instruments_and_effects.py`, these should already exist:
- Track 6 (or 10): Reverb Send (with Hybrid Reverb device)
- Track 7 (or 11): Delay Send (with Simple Delay device)

If not, create them manually:
1. Right-click in track area → "Create Track" → "Return Track" (x2)
2. Name one "Reverb Send", the other "Delay Send"
3. Add "Hybrid Reverb" to Reverb Send track
4. Add "Simple Delay" to Delay Send track

### Configure Reverb Send (Track 6/10)
- Device: Hybrid Reverb
- Settings for dub techno:
  - Size: Large (50-80%)
  - Decay: Long (3-5 seconds)
  - Diffusion: Medium
  - High Cut: Around 4000 Hz
  - Wet/Dry: 100% (send track only)

### Configure Delay Send (Track 7/11)
- Device: Simple Delay
- Settings for dub techno:
  - Sync: On
  - Time: 1/4 note or 1/8 note
  - Feedback: 40-60%
  - Wet/Dry: 100% (send track only)

### Send Routing Configuration

For each main track (0-5), create sends to Reverb and Delay:

**Track 0 (Kick)**:
- Send to Reverb: 0% (no reverb on kick)
- Send to Delay: 0% (no delay on kick)

**Track 1 (Sub-bass)**:
- Send to Reverb: 5-10% (just a touch)
- Send to Delay: 5-10% (subtle delays)

**Track 2 (Hi-hats)**:
- Send to Reverb: 20-30%
- Send to Delay: 20-30%

**Track 3 (Synth Pads)**:
- Send to Reverb: 40-50% (more reverb for atmosphere)
- Send to Delay: 40-50% (dub delays on pads)

**Track 4 (FX)**:
- Send to Reverb: 60-70%
- Send to Delay: 60-70%

**Track 5 (Dub Delays)**:
- Send to Reverb: 80-100%
- Send to Delay: 80-100% (max sends for echo)

### How to Create Sends in Ableton

1. Click on track's "Sends" button (shows sends section)
2. Click "Audio To" dropdown in Sends area
3. Select "Reverb Send"
4. Adjust send level (knob)
5. Click "+" to add second send → select "Delay Send"
6. Adjust second send level

---

## STEP 3: Set Mix Levels

Before recording, set initial track volume levels for good balance:

**Reference Levels** (these are starting points - adjust to taste):

- Master: 0.0 dB (reference)
- Track 0 (Kick): -6 to -8 dB
- Track 1 (Sub-bass): -3 to -6 dB
- Track 2 (Hi-hats): -12 to -15 dB
- Track 3 (Synth Pads): -18 to -24 dB
- Track 4 (FX): -15 to -20 dB
- Track 5 (Dub Delays): -12 to -15 dB
- Reverb Send: -15 dB
- Delay Send: -12 dB

**Tip**: Start with these, then fine-tune by ear during the 1-minute test.

---

## STEP 4: Enable Recording in Ableton

### Option A: Master Track Recording

1. In Session View, locate the Master track
2. Click the "Record Arm" button on Master (Shift+R shortcut)
3. Master will glow red when armed for recording

### Option B: Export During Playback

You can also export the entire session while automation plays:
1. File → Export Audio/Video
2. Select "Master" as source
3. Set format: WAV or MP3
4. Set sample rate: 44100 or 48000 Hz
5. Set bit depth: 16-bit or 24-bit
6. Set duration: "Loop" or specify 2:00:00
7. Click "Export"
8. Start automation script (below) when export begins

### Recording Location

The file will be saved to:
- **Windows**: `C:\Users\[YourName]\Documents\Ableton\Exports\`
- **Mac**: `~/Music/Ableton/Exports/`

---

## STEP 5: Run the 2-Hour Automation

### Start Recording

1. **Enable recording** in Ableton (Master arm or start export)
2. **Verify levels** - ensure no clipping (red lights)
3. **Run automation script**:

```bash
cd C:\Users\Tobias\git\ableton-mcp-extended
python dub_techno_2h/record_and_play_2h_dub_techno.py
```

4. **Press Enter** when prompted to start automation
5. **Wait 2 hours** - the script will:
   - Fire clips for each section (30 sections total)
   - Show progress with percentage bar
   - Display current section name and description
   - Automatically progress every 4 minutes

### What Happens During Automation

- **Sections 0-3** (0:00-0:16): Introduction - minimal buildup
- **Sections 4-7** (0:16-0:32): Hypnotic groove
- **Sections 8-11** (0:32-0:48): First buildup and peak
- **Sections 12-15** (0:48-1:04): Breakdown - atmosphere
- **Sections 16-19** (1:04-1:20): Second buildup
- **Sections 20-23** (1:20-1:36): Journey - sustained energy
- **Sections 24-27** (1:36-1:52): Final push to peak
- **Sections 28-29** (1:52-2:00): Wind down - fade out

### Progress Display

The console will show:
```
[00:00] Section 0 - Deep Intro
  Description: Minimal elements establish groove
  ✓ Clips fired

[00:16] Section 1 - Subtle Build
  Description: Adding slight variations, more delays
  ✓ Clips fired
```

Progress bar: `[=======================---------------] 50%`

### Stopping Early

To stop automation early (and recording):
- Press `Ctrl+C` in the console
- Immediately stop recording in Ableton
- Export any captured audio

---

## STEP 6: Finalize dubking.mp3

### If Recording Directly to Disk

1. Stop recording in Ableton (Space bar or Stop button)
2. File will be in Exports folder
3. Rename to `dubking.mp3` if not already named
4. Verify file size (should be ~100-200 MB for 2 hours at 320kbps MP3)

### If Exporting During Playback

1. Wait for Ableton export to complete
2. File will be in Exports folder
3. Rename to `dubking.mp3`
4. Verify file plays correctly

### Converting to MP3 (If Exported as WAV)

If you exported as WAV:
1. Use audio converter (Audacity, FFmpeg, online tools)
2. Command-line example:
   ```bash
   ffmpeg -i dubking.wav -codec:a libmp3lame -b:a 320k dubking.mp3
   ```
3. Quality: 320kbps for high quality MP3

---

## Troubleshooting

### No Sound from Tracks

**Problem**: Clips fire but no audio plays

**Solutions**:
1. Check instrument devices are on (not muted)
2. Verify track volume faders are up
3. Check track is not muted/soloed (mute button off)
4. Verify MIDI notes are triggering instruments (watch keyboard press visualization)
5. Ensure instruments have valid presets loaded

### Clips Not Firing

**Problem**: Script errors when trying to fire clips

**Solutions**:
1. Verify Ableton is running
2. Check Remote Script is loaded (Preferences → Link/Tempo/MIDI → Control Surface: AbletonMCP)
3. Verify clip indices are correct (0-7 for each track)
4. Check track indices are correct (0-5 for the 6 tracks)
5. Restart Ableton and try again

### Recording Is Silent

**Problem**: Recording starts but captures no audio

**Solutions**:
1. Verify Master track is armed for recording
2. Check Master volume is up
3. Ensure tracks are playing (watch clip triggers)
4. Verify audio device is correct (Preferences → Audio)
5. Check system audio output settings

### Automation Progresses Too Fast/Slow

**Problem**: Section timing is wrong

**Solutions**:
1. Verify tempo is 126 BPM
2. Check Ableton's global transport is not affected by external MIDI
3. Ensure no other automation is interfering
4. The script waits 240 seconds per section - this is correct for 4 minutes at 126 BPM

### Audio Clipping/Distortion

**Problem**: Master levels go into red

**Solutions**:
1. Lower track volumes immediately
2. Check send levels are not too high
3. Lower Master volume temporarily
4. Enable Compressor on Master track
5. Export again with lower levels

---

## Tips for Best Results

### Before Full 2-Hour Run

1. **Test thoroughly**: Run `test_playback_1min.py` multiple times
2. **Verify all instruments**: Each track should produce sound
3. **Check send routing**: Reverb and delay should be audible
4. **Monitor levels**: Watch for clipping throughout
5. **Save project**: File → Save Project (Ctrl+S)
6. **Close other apps**: Maximize system resources

### During Recording

1. **Monitor console**: Watch progress and section changes
2. **Listen actively**: Take notes on sections you like/dislike
3. **Don't touch Ableton**: Let automation run uninterrupted
4. **Watch CPU usage**: Ensure Ableton doesn't overload
5. **Check periodically**: Every 10-15 minutes, verify recording is active

### After Recording

1. **Listen back**: Play through the full 2-hour track
2. **Check transitions**: Note any abrupt section changes
3. **Verify audio quality**: No glitches, clicks, or pops
4. **Backup the file**: Copy to multiple locations
5. **Document settings**: Save your mix levels and presets for future

---

## Project Summary

**Total Duration**: 2 hours (120 minutes)
**Sections**: 30 sections × 4 minutes each
**Tracks**: 6 main tracks + 2 send tracks
**Clips**: 48 MIDI clips (8 per track)
**Tempo**: 126 BPM
**Key**: C minor with variations (Fm, Gm, Eb major)

**Output File**: `dubking.mp3`

---

## Automation Scripts Reference

### 1-Minute Test
```bash
python dub_techno_2h/test_playback_1min.py
```
Plays Section 0 for 1 minute. Use this to verify setup before full recording.

### 2-Hour Full Automation
```bash
python dub_techno_2h/record_and_play_2h_dub_techno.py
```
Automatically plays all 30 sections over 2 hours. Run this while recording in Ableton.

---

## Next Steps

1. **Configure instruments** in Ableton (Step 1)
2. **Set up sends** for reverb and delay (Step 2)
3. **Adjust mix levels** (Step 3)
4. **Enable recording** in Ableton (Step 4)
5. **Run test playback** to verify everything works
6. **Run full 2-hour automation** while recording
7. **Finalize dubking.mp3** from your export

---

## Support

If you encounter issues:

1. Check Ableton Live is version 11+ (required for Remote Script)
2. Verify Remote Script path: `Documents\Ableton\User Library\Remote Scripts\AbletonMCP`
3. Check Python version: Python 3.10+ required for automation scripts
4. Restart Ableton after configuration changes

**Resources**:
- Ableton Live Manual: https://help.ableton.com
- MCP Server Documentation: `MCP_Server/server.py` source code
- Remote Script Code: `AbletonMCP_Remote_Script/__init__.py`

---

## Summary

Your 2-hour dub techno project is ready for recording! Follow the steps above, run the automation script while Ableton is recording, and you'll have `dubking.mp3` - a complete 2-hour dub techno journey with 30 evolving sections, hypnotic grooves, and deep atmospheres.

**Estimated Total Time**:
- Instrument setup: 30-40 minutes
- Send routing: 5-10 minutes
- Mix balancing: 10-15 minutes
- Test playback: 2-3 minutes
- 2-hour recording: 2 hours
- **Total**: ~2.5 to 3 hours

Enjoy creating your dub techno masterpiece! 🎹
