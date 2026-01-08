# Max for Live Audio Export - Integration Guide

## Overview

This directory contains a Max for Live device (`audio_export_device.maxpat`) that enables audio recording and export capabilities within Ableton Live.

### ⚠️ Critical Limitation

**Remote Scripts CANNOT control Max devices.**

Communication is **one-way only**:
- ✅ Max devices → Ableton Live (works)
- ✅ Max devices → Remote Scripts (via Live API)
- ❌ Remote Scripts → Max devices (NOT possible)

This means the MCP server **cannot** automatically control the Max export device. Users must manually trigger recording through the device's interface.

---

## Device: audio_export_device.maxpat

### Capabilities

✅ **Direct Audio Export:**
- Export to WAV format (highest quality)
- Real-time audio capture from track input
- Toggle recording on/off
- Set output filename
- Set sample rate (44100/48000/96000 Hz)
- Set bit depth (16/24/32 bit)

❌ **Not Supported:**
- Direct MP3 export (use convert_to_mp3.py for conversion)
- Automatic triggering from Remote Scripts
- Bidirectional communication with MCP server

### Device Features

| Feature | Description | Control Method |
|----------|-------------|----------------|
| Start Recording | Begin audio capture | **Manual bang** (click) |
| Stop Recording | End capture, save file | **Manual bang** (click) |
| Set Filename | Change output file name | **Manual message** or patch |
| Set Format | Choose export format | Manual message (`setformat`) |
| Set Sample Rate | Configure audio quality | Manual message (`setsr`) |
| Set Bit Depth | Configure resolution | Manual message (`setbitdepth`) |
| List Files | Show recording status | Manual message (`listfiles`) |
| Info | Display help/instructions | Manual message (`info`) |

### Device Messages

**Toggle Recording:**
```
bang  (click the bang inlet)
```
- Starts recording if stopped
- Stops recording if active
- Saves audio to WAV file on stop

**Set Output File:**
```
setfile <filename>
```
Example: `setfile my_recording.wav`
- Automatically adds `.wav` if extension not provided
- File saves to Ableton's current project directory

**Set Format:**
```
setformat <format>
```
Supported formats:
- `wave` (default) - Standard WAV format
- `aiff` - AIFF format
- `ogg` - OGG format
- `flac` - Lossless compression
- `raw` - Raw audio data

**Set Sample Rate:**
```
setsr <rate>
```
Supported rates:
- `44100` (default) - CD quality
- `48000` - Professional audio
- `96000` - High-resolution

**Set Bit Depth:**
```
setbitdepth <bits>
```
Supported depths:
- `16` (default) - Standard CD quality
- `24` - High-resolution
- `32` - Floating-point

**Status Commands:**
```
listfiles  - Show current recording configuration
info        - Display full help text
```

---

## Installation

### 1. Copy Max Device to Ableton

1. Locate your Ableton Max Devices folder:
   - **Windows**: `C:\Users\[You]\Documents\Ableton\User Library\Packs\`
   - **Mac**: `~/Music/Ableton/User Library/Packs/`

2. Copy `audio_export_device.maxpat` to that folder

3. Open Ableton Live

4. Search in Browser → **Packs** → `audio_export_device`

### 2. Load Device on Track

**Method A: Browser**
1. Right-click track → **Insert audio effect**
2. Search in browser for `audio_export_device`
3. Click and drag onto track

**Method B: Drag & Drop**
1. Open browser → **Packs**
2. Find `audio_export_device`
3. Drag device directly onto track

---

## Usage Workflow

### Complete Audio Export Workflow

```
STEP 1: PREPARE SESSION
├─ Create audio track for export (MCP: create_audio_track)
├─ Load Max export device onto track
└─ Set output filename (optional, default: export.wav)

STEP 2: CAPTURE AUDIO
├─ Route other tracks to export track (using sends or routing)
├─ Arm the export device track (optional)
└─ Click device's bang inlet to START recording
   └─ Audio is captured in real-time to device

STEP 3: STOP & SAVE
└─ Click device's bang inlet to STOP recording
   └─ Audio is automatically saved to WAV file
      └─ File location: Ableton project directory

STEP 4: CONVERT TO MP3 (OPTIONAL)
└─ Use conversion utility: python max_devices/convert_to_mp3.py export.wav
   └─ Output: export.mp3 (320kbps quality)
```

### Recording Individual Clips

**Manual approach (most common):**

```
1. Load export device on dedicated track
2. Set output filename: setfile clip_name.wav
3. Play the clip you want to export
4. Click bang to start recording at clip start
5. Click bang to stop at clip end
6. WAV file created
7. Convert to MP3 if needed
```

### Recording Full Session

**Real-time capture approach:**

```
1. Route master output to export track
2. Start session playback
3. Click bang to start recording
4. Let session play through
5. Click bang to stop recording
6. Full session captured to WAV
7. Convert to MP3 if needed
```

---

## MP3 Conversion Tool

### convert_to_mp3.py

Python utility to convert WAV files to high-quality MP3.

**Features:**
- Batch conversion support (`--batch` or `*.wav` pattern)
- High-quality encoding (320kbps)
- Automatic sample rate detection
- Multi-channel support
- Size comparison reporting

**Prerequisites:**
```bash
pip install pydub
# FFmpeg must be in system PATH
```

**Usage:**

```bash
# Single file conversion
python convert_to_mp3.py recording.wav

# Custom output filename
python convert_to_mp3.py recording.wav mytrack.mp3

# Batch convert all WAVs in directory
python convert_to_mp3.py --batch . *.wav
```

**Example Output:**
```
🎵 Converting: recording.wav
📖 Loading WAV file...
ℹ️  Duration: 45.23 seconds
ℹ️  Channels: 2 (stereo)
ℹ️  Sample rate: 44100 Hz
🔄 Converting to MP3...
✅ Conversion complete!
📊 Input:  7.72 MB
📊 Output: 1.25 MB
📊 Compression: 83.8% reduction
```

---

## Limitations & Workarounds

### Remote Script Communication

**Problem:**
The Ableton MCP server cannot send commands TO Max devices because:
- Live API does not provide Remote Script → Max device communication path
- Communication is one-way (Max → Remote Script only)
- No bi-directional messaging system exists

**Workarounds:**

1. **Manual Triggering** (Recommended)
   - Use device's built-in bang inlet
   - Click to toggle recording
   - Most reliable approach

2. **Parameter Changes** (Alternative)
   - Max devices CAN respond to parameter changes
   - MCP server CAN set parameters on tracks
   - Could use parameter changes as trigger signals
   - Limited flexibility, requires device redesign

3. **Separate Max Patch Control** (Advanced)
   - Create standalone Max application
   - Connect via Max for Live API
   - Communicate with Ableton Live directly
   - Bypass Remote Script limitation
   - Complex setup, requires external Max runtime

### File Format Limitations

**WAV vs MP3:**
- Max device exports to WAV (lossless, larger files)
- MP3 conversion required for distribution (smaller files)
- Conversion time: ~10-30 seconds per minute of audio
- Quality loss: Minimal at 320kbps

**Recommendation:**
- Use WAV for: Master quality, further processing, archival
- Use MP3 for: Sharing, web upload, storage efficiency

---

## Comparison: Max Device vs Ableton Export

| Feature | Max Device | Ableton Native |
|----------|-------------|----------------|
| **Automation** | Manual trigger | ✅ Full API control |
| **Format Support** | WAV/AIFF/OGG/FLAC | ✅ MP3/WAV/all formats |
| **Export Speed** | Real-time | ✅ Fast offline rendering |
| **Quality Control** | Sample rate/bit depth | ✅ Full export options |
| **Session Integration** | Manual device loading | ✅ Native session export |
| **Ease of Use** | Requires manual clicking | ✅ Menu/keyboard shortcuts |

**Bottom Line:** The Max device provides **basic audio capture** for situations where you need to extract specific clips or capture performance in real-time. For full project export, use Ableton's native export dialog.

---

## Troubleshooting

### Device Not Found

**Problem:** `audio_export_device` not appearing in browser

**Solutions:**
1. Ensure file is in correct Packs directory
2. Rescan browser (right-click → "Rescan Packs")
3. Check Ableton Live version (requires Live 11+)
4. Try dragging .maxpat file directly onto track

### No Audio Captured

**Problem:** Recording starts but WAV file is empty/small

**Causes:**
- No audio routed to device's input
- Track muted
- Input monitoring off

**Solutions:**
1. Send audio from source track (using send or routing)
2. Unmute source track
3. Set track monitoring to "In" or "Auto"
4. Verify audio signal flow with meter

### MP3 Conversion Fails

**Problem:** `convert_to_mp3.py` reports missing dependencies

**Solutions:**
```bash
# Install pydub (includes FFmpeg dependency)
pip install pydub

# Or install FFmpeg separately
# Windows: Download from https://ffmpeg.org/download.html
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

---

## Advanced Workflows

### Recording Specific Loops

```
1. Set loop points on clip: 4-8 bars
2. Set output file: setfile loop_export.wav
3. Start playback at bar 4
4. Click bang to start recording
5. Loop plays 4 times (4-5, 5-6, 6-7, 7-8)
6. Click bang to stop at bar 9
7. Result: 4 loops captured in single WAV file
```

### Multi-Track Capture

```
Setup:
- Track 1: Drums → Send to Export Track
- Track 2: Bass → Send to Export Track
- Track 3: Synths → Send to Export Track
- Export Track: Has audio_export_device

Recording:
1. Click bang to start
2. All routed audio captured to single WAV
3. Click bang to stop
4. Use mixer or convert to separate stems if needed
```

---

## Integration with MCP Server

### What MCP CAN Do

While the MCP server cannot control the Max device directly, it can help prepare the session:

```python
# Create dedicated export track
create_audio_track(index=-1)
set_track_name(track_index=0, name="Audio Export")

# Route source tracks to export track
set_send_amount(track_index=5, send_index=0, amount=1.0)  # Send to return
# Configure return to send to export track (manual Ableton routing)

# Start/stop playback for recording
start_playback()
stop_playback()
```

### Manual Workflow Summary

```
1. MCP: Prepare session (tracks, routing, playback control)
2. Manual: Load Max export device
3. Manual: Configure device (filename, format)
4. Manual: Trigger recording (bang click)
5. Manual: Stop recording (bang click)
6. Optional: Convert WAV → MP3 using convert_to_mp3.py
```

**This hybrid approach provides:**
- ✅ Automated session preparation
- ✅ Quality audio capture (Max device)
- ✅ Real-time performance recording
- ✅ Flexible export format options
- ⚠️ Requires manual recording triggers

---

## File Locations

**After recording:**
- **WAV files**: Saved to Ableton project directory
- **MP3 files**: Saved to same directory (after conversion)
- **Default location**: `~/Documents/Ableton/Projects/[ProjectName]/`

**Finding recordings:**
1. Ableton File Browser → **Samples**
2. System file manager
3. Use Ableton's File > Show in Finder/Explorer

---

## Support & Resources

**Max for Live Documentation:**
- Max SDK: https://docs.cycling74.com/max-sdk/
- File I/O: https://docs.cycling74.com/max-sdk/filesystem.html
- sfrecord~: https://docs.cycling74.com/reference/sfrecord~/

**Ableton Live Resources:**
- User Manual: https://www.ableton.com/en/manual/live11/
- Forum: https://forum.ableton.com/viewforum.php?f=49

**Community Projects:**
- Max4Live: https://github.com/timo-schneiding/max4live
- Max for Live Tutorials: https://adammurray.link/max-for-live/

---

*Last Updated: January 2026*
*Compatible with Ableton Live 11+*
