# Ableton MCP Server - Export Functionality Limitations

## Summary

**Critical Understanding**: Ableton Live's Python Remote Script API does NOT support direct audio export (MP3/WAV) or saving audio files to disk.

## What IS NOT Supported

### ❌ Export to MP3/WAV
- No API method to export audio to MP3 format
- No API method to export audio to WAV format
- Cannot trigger Ableton's built-in export dialog programmatically
- Cannot access project export settings

### ❌ Save Audio Files
- No API method to save audio clips to files
- No API method to extract audio data from clips
- No file I/O access for arbitrary read/write operations
- Cannot save recorded audio to a specific file path

### ❌ Resample/Bounce Workarounds via API
- While you can create resample tracks and control recording, this is:
  - Real-time only (not batch export)
  - Requires manual intervention to stop and save
  - Not a programmatic export solution

## Why These Limitations Exist

### Ableton Remote Script API Design
The Remote Script API (Live Object Model - LOM) is designed to:
- Control playback, recording, and session state
- Manipulate tracks, clips, devices, and parameters
- Access browser and load instruments/effects
- Read song structure and properties

It is **NOT** designed to:
- Perform file I/O operations
- Access export/bounce functionality
- Trigger GUI dialogs or menus
- Extract raw audio data from clips

### Security and Stability
Ableton intentionally restricts:
- File system access (prevents malicious scripts)
- Export functionality (prevents automated rendering without user awareness)
- GUI control (prevents scripts from interfering with user interaction)

## What IS Supported (Recording)

### ✅ Recording Control
The following recording functions ARE implemented and working:

```python
# Start recording (starts playback if needed)
start_recording()

# Stop recording (playback continues)
stop_recording()
```

**How recording works:**
1. Track(s) must be armed for recording (use `set_track_arm`)
2. Recording starts playback if not already playing
3. Audio is captured in real-time to armed tracks
4. Recording stops but playback continues
5. Audio remains in Ableton session (requires manual save/export)

### ✅ Recording Workflow (Manual Export Required)

```python
# Step 1: Create and arm audio track
create_audio_track(index=0)
set_track_arm(track_index=0, arm=True)

# Step 2: Start recording
start_recording()

# Step 3: Play your session (via clips or instruments)
fire_clip(track_index=1, clip_index=0)

# Step 4: Stop recording after desired duration
stop_recording()
set_track_arm(track_index=0, arm=False)

# Step 5: MANUAL EXPORT REQUIRED
# User must now:
# 1. Select the recorded clip in Ableton
# 2. Right-click and choose "Export"
# 3. Configure export settings
# 4. Save to desired format (MP3/WAV)
```

## Workarounds and Alternatives

### 1. GUI Automation Tools (External)
Projects that simulate user actions to trigger export:

- **[ableton-export-bot](https://github.com/hankijord/ableton-export-bot)**
  - Simulates keyboard shortcuts
  - Triggers export dialog via Ctrl+Shift+E
  - Navigates UI to confirm export
  - **Limitation**: Fragile, screen resolution dependent

- **[AbletonLiveAutoExporter](https://github.com/ntn98/AbletonLiveAutoExporter)**
  - Uses keyboard automation (pyautogui/pywinauto)
  - Automates export workflow end-to-end
  - **Limitation**: Requires visible Ableton window, prone to breaking

### 2. Resampling Method (Semi-Automated)
Workflow that combines MCP control with manual action:

```python
# Step 1: Create new audio track for resampling
create_audio_track(index=-1)
set_track_name(track_index=new_track_index, name="Resample Output")

# Step 2: Set track to Resample source
# (This must be done manually in Ableton UI)
# Right-click track > Set Input to > Resampling

# Step 3: Route other tracks to resample track
# (Use sends or master routing)

# Step 4: Record in real-time
set_track_arm(track_index=new_track_index, arm=True)
start_recording()
# Play source tracks...

# Step 5: Stop and save manually
stop_recording()
# User must manually right-click the recorded clip > Export
```

### 3. Max for Live (Internal)
Max devices can record and export audio:

```max
// Max For Live device example
[buffer~ recording_buffer]
[record~ 1]
[write recording_buffer export.wav]
```

**Limitation**: Only works within Max device context, not general Remote Scripts.

### 4. External Audio Capture (Alternative Approach)
Record Ableton's output using system audio:

```python
# Use Python libraries like:
# - pyaudio (direct audio capture)
# - sounddevice (cross-platform)
# - pydub (audio processing)

import sounddevice as sd
import numpy as np
import wavio

# Record system audio (requires routing Ableton output to system out)
def record_system_audio(duration, filename):
    fs = 44100
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    wavio.write(filename, recording, fs, sampwidth=2)
```

**Limitation**: System-level capture, not integrated with Ableton's project.

## Community Feedback and Status

### Current Status (2025)
- ✅ No API changes to add export functionality
- ✅ No official statements about planned export API additions
- ✅ Community consensus: Export requires GUI automation or manual action
- ✅ Multiple open-source projects attempting workarounds

### Ableton Forum Discussions
Key findings from official Ableton forums:

- **Remote Script API intentionally limited**: "LOM is for control, not rendering"
- **Export functions not exposed**: "No way to trigger File > Export from Python"
- **File I/O restricted**: "Scripts cannot write to arbitrary paths for security"

## Recommendations for Users

### If You Need Audio Export

1. **Max for Live Device** (Recommended - Included!)
   - Use provided Max device (`max_devices/audio_export_device.maxpat`)
   - Load device onto track in Ableton
   - Manually trigger recording via device's bang inlet
   - Real-time WAV export directly from Ableton
   - See [max_devices/README.md](max_devices/README.md) for details
   - ✅ Best for: Clip capture, performance recording, loop recording

2. **Manual Export** (Most Reliable for Full Sessions):
   - Use MCP to prepare and record session
   - Export manually via Ableton's File > Export menu
   - Full control over quality, format, and settings
   - ✅ Best for: Complete project export, multiple formats (MP3/WAV)

3. **Resampling Workaround** (For Quick Captures):
   - Record to resampling track in real-time
   - Export just that clip (faster than full session export)

4. **GUI Automation** (For Bulk Operations):
   - Use external tools like ableton-export-bot
   - Accept fragility and UI dependencies
   - Best for: Repetitive export tasks, batch operations

5. **System Audio Capture** (For Prototyping):
   - Use Python audio libraries
   - Route Ableton to system output
   - Independent of Ableton project structure
   - ⚠️ Not integrated with Ableton project

## API Limitations Reference

### File Operations
- ❌ Read arbitrary files
- ❌ Write arbitrary files
- ❌ Access user file system
- ✅ Ableton project save (via `.save()` on Song object)

### Export Operations
- ❌ Export to MP3
- ❌ Export to WAV
- ❌ Export to any format
- ❌ Bounce selection
- ❌ Render track
- ✅ Record audio to armed tracks (real-time)

### GUI Control
- ❌ Trigger menu items
- ❌ Simulate keyboard input
- ❌ Access export dialog
- ✅ Show messages in Ableton status bar

## Conclusion

**The Ableton Live Remote Script API is fundamentally designed for session control and manipulation, not for audio rendering or export operations.**

For audio export functionality, users must:
1. **Use manual export** (File > Export) after recording with MCP
2. **Employ external GUI automation** tools (with acknowledged limitations)
3. **Consider system-level audio capture** (non-integrated workaround)

The MCP server provides all recording control necessary to prepare for manual export:
- ✅ `start_recording()` - Start real-time capture
- ✅ `stop_recording()` - End recording session
- ✅ `set_track_arm()` - Arm tracks for recording
- ✅ `create_audio_track()` - Prepare destination tracks

**No further export functionality is possible through Ableton's API.**

---

*Document based on research of Ableton Live 11+ Remote Script API, official documentation, and community projects as of January 2026.*
