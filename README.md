# Ableton MCP Extended

**Control Ableton Live using natural language via AI assistants like Claude or Cursor.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Ableton Live 11+](https://img.shields.io/badge/Ableton%20Live-11+-orange.svg)](https://www.ableton.com/)

---

Video demonstration: https://www.youtube.com/watch?v=7ZKPIrJuuKk

This tool is designed for producers, developers, and AI enthusiasts who want to streamline their music production workflow, experiment with generative music, and build custom integrations with Ableton Live.

---

## 🎵 NEW: 2-HOUR DUB TECHNOPO PROJECT

**Automated 2-hour dub techno track - hands-free playback!**

### Quick Start (3 steps, 40 minutes setup, 2 hours automation)

```bash
# 0. go to dub_techno_2h folder
cd dub_techno_2h

# 1. Create everything
python create_2h_dub_techno_fixed.py
python load_instruments_and_effects.py

# 2. Manual setup (30-40 minutes)
# - Configure instrument presets in Ableton
# - Set up send routing
# - Set initial mix levels
# - Configure effects (reverb, delay)

# 3. Run full 2-hour automation
python auto_play_2h_dub_techno.py
```

### What You Get

✅ **Complete 2-hour dub techno track**
- 12 tracks (6 main + 2 sends)
- 48 MIDI clips (8 per track)
- 30 sections (4 minutes each)
- Full automation system
- Comprehensive documentation (5 files)

### Automation Features

- ✅ Automatic scene progression (timer-based, every 4 minutes)
- ✅ Filter automation on synth pads (400-2000 Hz sweeps)
- ✅ Track volume changes per section
- ✅ Progress tracking with visual progress bar
- ✅ Graceful stopping (Ctrl+C support)
- ✅ Error recovery (continues despite failures)

### Files Created

**Scripts (3 files)**:
- `create_2h_dub_techno_fixed.py` - Creates tracks and clips
- `load_instruments_and_effects.py` - Loads instruments and effects
- `auto_play_2h_dub_techno.py` - **FULL AUTOMATION** ⭐

**Documentation (2 files)**:
- `DUB_TECHNO_2H_COMPLETE_GUIDE.md` - Configuration guide
- `DUB_TECHNO_2H_COMPLETE_SUMMARY.md` - Complete summary

**Total**: 9 files, ~3,500+ lines of code and docs

---

## Key Features

### 🎹 Session and Transport Control
* Start and stop playback
* Get session info, including tempo, time signature, and track count
* Manage scenes: create, delete, rename, and fire

### 🎛️ Track Management
* Create, rename, and get detailed information for MIDI and audio tracks
* Control track properties: volume, panning, mute, solo, and arm
* Manage track grouping and folding states

### 🎹 MIDI Clip and Note Manipulation
* Create and name MIDI clips with specified lengths
* Add, delete, transpose, and quantize notes within clips
* Perform batch edits on multiple notes in a single operation
* Adjust clip loop parameters and follow actions

### 🎚️ Device and Parameter Control
* Load instruments and effects from Ableton's browser by URI
* Get a full list of parameters for any device on a track
* Set and batch-set device parameters using normalized values (0.0 to 1.0)
* Automation: Add and clear automation points for any device parameter within a clip
* Load presets for devices on tracks by name (case-insensitive search)

* **NEW: Delete devices** - Remove effects/instruments from tracks
* **NEW: Duplicate devices** - Copy devices to other tracks
* **NEW: Move devices** - Reorder devices in the chain
* **NEW: Toggle device bypass** - Enable/disable effects on/off

### 🌊 Browser Integration
* Navigate and list items from Ableton's browser
* Load instruments, effects, and samples directly from a browser path or URI
* Import audio files directly into audio tracks or clip slots

### 🎤 Voice & Audio Generation
* Text-to-Speech Integration: Generate narration, vocal samples, or spoken elements through ElevenLabs MCP
* Custom Voice Creation: Clone voices for unique character in your tracks
* Sound Effects: Create custom SFX with AI
* Direct Import: Generated audio appears instantly in your Ableton session

### 🎛️ Extensible Framework for Custom Tools
* Example: XY Mouse Controller: Demonstrates creating custom Ableton controllers with MCP framework
* Ultra-Low Latency: High-performance UDP protocol enables responsive real-time control
* Unlimited Possibilities: Build your own custom tools and controllers for Ableton Live
* **NEW: Max for Live Audio Export Device**: Real-time WAV export for clips and performance recording
  * See [max_devices/](#max-for-live-audio-export-device) for details
* **NEW: Clip Operations** - Move, resize, and crop clips with precision
* **NEW: Device Management** - Delete, duplicate, move, and bypass effects/instruments
* **NEW: Clip Renaming** - Set clip names for organization

---

## ❌ Important: Audio Export Limitations

**Please read [EXPORT_LIMITATIONS.md](EXPORT_LIMITATIONS.md) before attempting to export audio.**

### What is NOT Supported
Due to Ableton Live's Remote Script API design, the following are **fundamentally impossible**:

* ❌ **Export to MP3/WAV** - No API method exists to export audio to files
* ❌ **Save Audio Files** - No API method exists to save audio clips to disk
* ❌ **Trigger Export Dialog** - Cannot programmatically trigger File > Export menu
* ❌ **Extract Audio Data** - Cannot extract raw audio from clips programmatically

### What IS Supported
The recording workflow IS supported:

* ✅ **start_recording** - Start real-time recording (plays if needed)
* ✅ **stop_recording** - Stop recording (playback continues)
* ✅ **set_track_arm** - Arm tracks for recording
* ✅ **create_audio_track** - Create destination tracks for recording

### How to Export Audio (Required Manual Step)
After recording with MCP tools, you must **manually export** in Ableton:

1. Select the recorded clip in Ableton
2. Right-click → **Export**
3. Choose format (MP3/WAV) and settings
4. Save to desired location

**See [EXPORT_LIMITATIONS.md](EXPORT_LIMITATIONS.md) for complete details, workarounds, and explanations.**

### 🎛️ Max for Live Audio Export Device

**NEW: Max for Live device for audio export!**

We've included a Max for Live device (`max_devices/audio_export_device.maxpat`) that provides audio recording capabilities.

**What It Can Do:**
- ✅ **Direct WAV export** - Record and save to WAV format in real-time
- ✅ **Multiple formats** - WAV, AIFF, OGG, FLAC, RAW support
- ✅ **Quality control** - Configure sample rate (44100/48000/96000) and bit depth (16/24/32)
- ✅ **Real-time capture** - Record live performance or clips as they play

**Critical Limitation:**
- ❌ **No Remote Script control** - Must manually trigger via device interface (click)
- ❌ **No MP3 export** - Export to WAV, use conversion tool for MP3

**Usage:**
1. Load device onto track in Ableton (Browser → Packs → audio_export_device)
2. Route audio to device input (sends or routing)
3. Configure output filename (send `setfile <name>` to device)
4. Click device's **bang inlet** to start/stop recording
5. WAV file saved automatically
6. Convert to MP3: `python max_devices/convert_to_mp3.py export.wav`

**See [max_devices/README.md](max_devices/README.md) for complete Max device documentation and workflows.**

---

## Project Structure

```
ableton-mcp-extended/
├── MCP_Server/                      # Core MCP server implementation
│   └── server.py                   # FastMCP server with tools
│
├── AbletonMCP_Remote_Script/       # Ableton Live Remote Script
│   └── __init__.py                 # Socket server & command handler
│
├── dub_techno_2h/                  # 2-hour dub techno automation scripts
│   ├── create_2h_dub_techno_fixed.py  # Creates tracks and clips
│   ├── load_instruments_and_effects.py # Loads instruments and effects
│   ├── auto_play_2h_dub_techno.py     # Full 2-hour automation
│   ├── automate_all_setup.py          # All-in-one setup script
│   ├── archive/                       # Older versions and deprecated scripts
│   └── DUB_TECHNO_2H_*.md            # Documentation files
│
├── scripts/                         # Utility and test scripts
│   ├── test/                        # Test scripts
│   │   ├── test_connection.py
│   │   ├── test_clip_firing.py
│   │   └── test_playback_1min.py
│   └── util/                        # Utility scripts
│       ├── check_session_state.py
│       ├── check_tracks.py
│       ├── create_percussion.py
│       ├── get_effects.py
│       ├── new_device_methods.py
│       ├── record_dub_song_automated.py
│       ├── record_dub_song_now.py
│       └── section_switcher.py
│
├── elevenlabs_mcp/                   # ElevenLabs integration
│   └── server.py                    # ElevenLabs MCP server
│
└── experimental_tools/                  # Examples and experimental tools
    └── xy_mouse_controller/
        ├── mouse_parameter_controller_udp.py  # XY mouse controller
        └── README.md
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Ableton Live 11+ (any edition)
- Python 3.10 or higher
- Claude Desktop or Cursor IDE

### 1. **Get the Code**
```bash
git clone https://github.com/uisato/ableton-mcp-extended.git
cd ableton-mcp-extended
pip install -e .
```

### 2. **Install Ableton Script**
1. Find your Ableton Remote Scripts folder:
   - **Windows**: `C:\Users\[You]\Documents\Ableton\User Library\Remote Scripts\`
   - **Mac**: `~/Library/Preferences/Ableton/Live [Version]/User Remote Scripts/`
2. Create folder: `AbletonMCP`
3. Copy `AbletonMCP_Remote_Script/__init__.py` into this folder

### 3. **Configure Ableton**
1. Open Ableton Live
2. Go to **Preferences** → **Link, Tempo & MIDI**
3. Set **Control Surface** to "AbletonMCP"
4. Set Input/Output to "None"

### 4. **Connect AI Assistant**

**For Claude Desktop:**
```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "python",
      "args": ["C:/path/to/ableton-mcp-extended/MCP_Server/server.py"]
    }
  }
}
```

**For Cursor:**
Add MCP server in Settings → MCP with the same path.

### 5. **Start Creating!** 🎹
Open your AI assistant and try:
- *"Create a new MIDI track with a piano"*
- *"Add a simple drum beat"*
- *"What tracks do I currently have?"*

---

## 🎵 2-HOUR DUB TECHNOPO - DETAILED GUIDE

### Project Overview

**Type**: 2-hour automated dub techno track
**Tempo**: 126 BPM
**Duration**: 120 minutes (30 sections × 4 minutes)
**Tracks**: 12 total (6 main + 2 sends + 4 original)
**MIDI Clips**: 48 clips (8 per main track)

### Track Structure

| Track | Name | Type | Instruments | Effects | Purpose |
|-------|-------|------|-------------|----------|
| 4 | **Kick** | MIDI | Operator, EQ, Compressor | Punchy 4/4 kick pattern |
| 5 | **Sub-bass** | MIDI | Synth, EQ, Compressor | Deep, hypnotic bass drones |
| 6 | **Hi-hats** | MIDI | Drum Rack, EQ | Sparse, syncopated hi-hats |
| 7 | **Synth Pads** | MIDI | Wavetable, EQ, Auto Filter | Atmospheric chord pads |
| 8 | **FX** | MIDI | Simpler, EQ | Sweeps, impacts, risers |
| 9 | **Dub Delays** | MIDI | Utility | Send track for echo effects |
| 10 | **Reverb Send** | Audio | Hybrid Reverb | Returns reverb tails |
| 11 | **Delay Send** | Audio | Simple Delay | Returns dub delays |

### Section Structure

| Phase | Sections | Time | Energy | Characteristics |
|-------|-----------|-------|---------|-----------------|
| 1: Introduction | 0-3 | 0:00-0:16 | Minimal | Establish groove, dark atmosphere |
| 2: Hypnotic | 4-7 | 0:16-0:32 | Groove | Full groove, subtle evolution |
| 3: First Build | 8-11 | 0:32-0:48 | Building | Increasing energy to first peak |
| 4: Breakdown | 12-15 | 0:48-1:04 | Space | Removing elements, atmospheric |
| 5: Second Build | 16-19 | 1:04-1:20 | Building | Energy returns after breakdown |
| 6: Journey | 20-23 | 1:20-1:36 | Hypnosis | Sustaining groove, subtle changes |
| 7: Final Push | 24-27 | 1:36-1:52 | Peak | Maximum movement, complex layers |
| 8: Wind Down | 28-29 | 1:52-2:00 | Fading | Stripping back, fading out |

---

## 🤖 Automation System

### Features Implemented

#### ✅ Fully Automated

**1. Automatic Scene Progression**
- Timer-based progression every 4 minutes
- 30 sections over 2 hours
- Automatic clip firing
- Progress tracking with visual bar
- Graceful stopping (Ctrl+C)

**2. Device Parameter Control**
- Normalized values (0.0-1.0)
- Per-device parameter control
- Works with all device types

**3. Track Volume Automation**
- dB input with automatic normalization
- Section-specific volume targets
- Smooth transitions between sections

**4. Filter Automation (Synth Pads)**
- Auto Filter frequency sweeps
- Range: 400-2000 Hz
- Section-specific values

**5. Progress Tracking**
- Visual progress bar: `[======---] XX%`
- Elapsed time: HH:MM format
- Current section name and description

**6. Error Recovery**
- Warnings for parameter errors
- Continues execution despite failures
- No crashes or hanging

#### ⚙️ Partially Automated

**Send Level Automation**
- Informational targets printed
- Manual setup required in Ableton
- Target values shown for each section

#### ❌ Manual Setup Required

**Instrument Presets**
- Choose sounds in Ableton UI
- Per-track configuration needed

**Send Routing**
- Configure in Ableton mixer section
- Manual sends to tracks 10-11

**Effect Configuration**
- Reverb and delay parameters
- Manually adjust for best results

---

## 📚 Documentation

### Quick Reference

1. **`README.md`** (This file)
   - Project overview
   - 2-hour dub techno quick start
   - File structure

2. **`DUB_TECHNO_2H_OVERVIEW.md`**
   - Detailed project overview
   - Section timeline
   - Track and clip descriptions

3. **`DUB_TECHNO_2H_COMPLETE_GUIDE.md`**
   - Configuration guide
   - Instrument preset settings
   - Effect parameters
   - Send routing setup
   - Mix level targets
   - Automation strategies

4. **`DUB_TECHNO_2H_AUTOMATION_DOCS.md`**
   - Automation features documentation
   - Function descriptions
   - What's automated vs manual

5. **`DUB_TECHNO_2H_COMPLETE_SUMMARY.md`**
   - Complete project summary
   - File index
   - Statistics
   - Troubleshooting

---

## 🎼 Usage Examples

### Basic Commands

**Get Session Info:**
```python
python -c "import socket, json; s = socket.socket(); s.connect(('localhost', 9877)); s.send(json.dumps({'type': 'get_session_info', 'params': {}}).encode('utf-8')); print(json.loads(s.recv(8192).decode('utf-8'))); s.close()"
```

**Create Track:**
```python
python -c "import socket, json; s = socket.socket(); s.connect(('localhost', 9877)); s.send(json.dumps({'type': 'create_midi_track', 'params': {'index': -1}}).encode('utf-8')); print(json.loads(s.recv(8192).decode('utf-8'))); s.close()"
```

**Set Tempo:**
```python
python -c "import socket, json; s = socket.socket(); s.connect(('localhost', 9877)); s.send(json.dumps({'type': 'set_tempo', 'params': {'tempo': 126.0}}).encode('utf-8')); print(json.loads(s.recv(8192).decode('utf-8'))); s.close()"
```

**Start Playback:**
```python
python -c "import socket, json; s = socket.socket(); s.connect(('localhost', 9877)); s.send(json.dumps({'type': 'start_playback', 'params': {}}).encode('utf-8')); print(json.loads(s.recv(8192).decode('utf-8'))); s.close()"
```

### Run Full 2-Hour Automation

```bash
python auto_play_2h_dub_techno.py
```

---

## 🎯 Perfect For

* **🎧 Deep listening and meditation** - Hypnotic, evolving sounds
* **🧘 Yoga or focused work** - Background atmosphere
* **📻 Creative coding or writing** - Non-intrusive dub groove
* **🌙 Late-night sessions** - Long-form ambient/dub experience
* **🎛️ DJ sets and live performance** - Source material for mixing

---

## 🔧 Troubleshooting

### Common Issues

**"Could not connect to Ableton"**
- Make sure Ableton Live is open
- Check Remote Script is loaded (Preferences → Link, Tempo & MIDI → Control Surface: AbletonMCP)
- Verify Remote Script location

**"Socket connection refused"**
- Restart Ableton Live
- Re-run automation script

**"Clips don't fire"**
- Verify all 48 clips were created
- Re-run `create_2h_dub_techno.py`

**"Filter automation doesn't work"**
- Check Auto Filter device is on Track 7
- May need to adjust device index in script

**"No audible changes during automation"**
- Verify send routing is configured in Ableton
- Check volume faders actually move in Ableton UI
- Monitor CPU usage

---

## 🚧 Advanced Features

### High-Performance Mode (UDP Server)

For real-time parameter control with ultra-low latency:

```bash
# Install the hybrid server
cp -r Ableton-MCP_hybrid-server/AbletonMCP_UDP/ ~/Remote\ Scripts/AbletonMCP_UDP/

# Try the XY Mouse Controller example
cd experimental_tools/xy_mouse_controller
python mouse_parameter_controller_udp.py
```

This demonstrates how to build:
- Custom real-time controllers for Ableton
- Expressive performance tools
- Interactive music applications

### ElevenLabs Voice Integration

This repository can be integrated with other MCP servers, such as one for ElevenLabs, to generate and import audio directly into your project.

---

## 📊 Project Statistics

**Code**:
- Total scripts: 4 automation scripts
- Total documentation: 5 Markdown files
- Total lines: ~3,500+

**2-Hour Dub Techno**:
- Total duration: 120 minutes (2 hours)
- Total sections: 30
- Total tracks: 12
- Total MIDI clips: 48
- Automation functions: 8 core functions

---

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Share your creations

---

## 📜 License & Credits

**License**: MIT License - see [LICENSE](LICENSE) for details

**Built with:**
- [Model Context Protocol](https://github.com/modelcontextprotocol) - AI integration framework
- [ElevenLabs API](https://elevenlabs.io) - Professional voice generation
- [Ableton Live](https://www.ableton.com) - Digital audio workstation

**Inspired by:** The original [ableton-mcp](https://github.com/ahujasid/ableton-mcp) project

---

## 📢 Support & Community

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Share your creations and get help
- **YouTube**: [Video demonstration](https://www.youtube.com/watch?v=7ZKPIrJuuKk)

### Share Your Creations
Tag me with your AI-generated experiments! I love seeing what the community creates:

[YouTube](https://www.youtube.com/@uisato_) |
[Instagram](https://www.instagram.com/uisato_) |
[Patreon](https://www.patreon.com/c/uisato) |
[Website](https://www.uisato.art/)

---

<div align="center">

**Made with ❤️ for the music production community**

*If this project helps your creativity, consider giving it a ⭐ star!*

</div>
