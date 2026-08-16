# Production Pipeline - Complete Workflow Guide

> **From Mix Creation to YouTube Upload in One Command**

---

## 🚀 **OVERVIEW**

The **Production Pipeline** is a **complete, end-to-end** system that automates the entire process of:

1. ✅ **Mix Creation** - Generate structured arrangements for any genre
2. ✅ **Ableton Setup** - Configure tracks, volumes, panning, locators
3. ✅ **Optional Capture** - Record scenes in real-time
4. ✅ **Professional Polish** - Balance levels, optimize stereo, add automation
5. ✅ **Audio Export** - Export to WAV and convert to MP3
6. ✅ **Video Creation** - Generate waveform visualization videos
7. ✅ **YouTube Upload** - Upload to YouTube with metadata (OpenMusic-style)

---

## 🎯 **QUICK START**

### **Install Dependencies**

For **basic functionality** (mix creation, MP3 conversion):
```bash
# FFmpeg for audio processing (MP3 conversion)
# Windows: Download from https://ffmpeg.org/
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# LAME for MP3 (alternative)
# Mac: brew install lame
# Linux: sudo apt install lame
```

For **video creation**:
```bash
# FFmpeg already includes video capabilities
```

For **YouTube upload**:
```bash
# Install youtube-upload (optional)
pip install youtube-upload

# Or configure Google API:
# 1. Enable YouTube Data API
# 2. Create OAuth credentials
# 3. Save as youtube_client_secrets.json
```

---

## 📖 **USAGE EXAMPLES**

### **1. Create Dub Techno Mix & Export to MP3**

```bash
# Simple: Setup + Polish + Export to MP3
python scripts/production_pipeline.py dub_techno --mp3
```

**What happens:**
1. Creates Dub Techno structure in Ableton (9 sections, 272 bars)
2. Configures 8 tracks with appropriate volumes and panning
3. Creates locators at section boundaries
4. Polishes the mix (auto-balance, stereo, automation)
5. Guides you through WAV export from Ableton
6. Converts WAV to MP3 automatically
7. Saves MP3 to `exports/audio/`

---

### **2. Create Techno Mix with Video**

```bash
# Techno mix with waveform video
python scripts/production_pipeline.py techno --mp3 --video --title "My Techno Mix"
```

**What happens:**
1. Creates techno structure (9 sections, 240 bars, 128 BPM)
2. Sets up Ableton tracks and locators
3. Applies polish for professional sound
4. Exports to WAV (manual step)
5. Converts to MP3
6. Creates waveform visualization video
7. Saves video to `exports/video/`

---

### **3. Full Automation with Capture**

```bash
# Complete hands-off (requires manual scene triggering)
python scripts/production_pipeline.py dub --capture --mp3 --polish
```

**What happens:**
1. Creates dub structure
2. Guides you to start recording in Ableton
3. You manually trigger scenes following the locators
4. After capture, polishes the mix
5. Converts to MP3
6. All automated!

---

### **4. Custom Mix with YouTube Upload**

```bash
# Custom house mix with YouTube upload
python scripts/production_pipeline.py custom --genre house --bpm 120 --mp3 --video --youtube \
    --title "House Mix July 2026" \
    --artist "My DJ Name" \
    --description "Generated with Ableton MCP Extended"
```

**What happens:**
1. Creates custom house structure at 120 BPM
2. Sets up Ableton
3. Polishes, exports, converts to MP3
4. Creates waveform video
5. Uploads to YouTube with your metadata
6. Provides video URL

---

## 📚 **COMMAND LINE REFERENCE**

### **Basic Usage**

```bash
# Show help
python scripts/production_pipeline.py --help

# Dry run (show what would happen)
python scripts/production_pipeline.py dub_techno --dry-run
```

### **Positional Arguments**

| Argument | Choices | Description |
|----------|---------|-------------|
| `mix_type` | `dub_techno`, `dub`, `techno`, `hiphop`, `house`, `dnb`, `ambient`, `custom` | The type of mix to create |

### **Options**

#### **Project Customization**
| Option | Description | Default |
|--------|-------------|---------|
| `--name NAME` | Project name (auto-generates timestamp if not provided) | auto |
| `--genre GENRE` | Genre for custom mixes (required if mix_type=custom) | - |
| `--bpm BPM` | BPM override | genre default |

#### **Pipeline Control**
| Option | Description | Default |
|--------|-------------|---------|
| `--capture` | Enable capture mode (you manually trigger scenes) | No |
| `--no-polish` | Skip automatic polish pass | Polish enabled |
| `--mp3` | Convert to MP3 | No |
| `--video` | Create waveform video | No |
| `--youtube` | Upload to YouTube | No |

#### **Metadata**
| Option | Description | Default |
|--------|-------------|---------|
| `--title TITLE` | Mix title (auto-generates from genre if not provided) | auto |
| `--artist ARTIST` | Artist name | Ableton MCP Extended |
| `--description DESCRIPTION` | Description (for YouTube) | auto |

#### **Other**
| Option | Description |
|--------|-------------|
| `--dry-run` | Show configuration without executing |

---

## 🎨 **AVAILABLE MIX TYPES**

### **Pre-Configured Genres**

| Mix Type | Genre | BPM | Sections | Duration | Style |
|----------|-------|-----|----------|----------|-------|
| `dub_techno` | **Dub Techno** | 125 | 9 | ~11 min | Deep sub-bass + 4/4 kick |
| `dub` | **Dub** | 75 | 9 | ~22 min | Echo, reverb, filter sweeps |
| `techno` | **Techno** | 128 | 9 | ~11 min | Pounding kicks, atmospheric |
| `hiphop` | **Hip-Hop** | 85 | 8 | ~10 min | Punchy drums, sidechain |
| `house` | **House** | 120 | 9 | ~8 min | Four-on-floor, disco |
| `dnb` | **Drum & Bass** | 174 | 9 | ~7 min | Breakbeats, wobble bass |
| `ambient` | **Ambient** | 60 | 9 | ~43 min | Slow, evolving, atmospheric |

### **Custom Mixes**

```bash
# Create a custom mix with any genre at any BPM
python scripts/production_pipeline.py custom --genre hiphop --bpm 90 --mp3
```

---

## 🎛️ **PIPELINE STEPS EXPLAINED**

### **Step 1: Project Creation**
- Generates mix structure based on genre
- Calculates duration, BPM, energy flow
- Creates section blueprint

### **Step 2: Ableton Setup**
- Sets tempo (default or custom BPM)
- Creates locators at section boundaries
- Configures track names, volumes, panning
- Sets master volume with headroom

### **Step 3: Optional Capture** (if `--capture`)
- Guides you to arm tracks and start recording
- You manually trigger scenes in sequence
- Follows the locator timeline
- Press Enter when capture is complete

### **Step 4: Polish** (if not `--no-polish`)
- Runs `polish_suite.py full` with genre presets
- Balances track levels intelligently
- Optimizes stereo image
- Adds automation to FX/melody tracks
- Prepares for export

### **Step 5: WAV Export**
- **Manual step**: You must export from Ableton
- Guides you through File -> Export Audio/Video...
- Specifies format, bit depth, sample rate
- Uses locators for range
- Waits for you to complete export

### **Step 6: MP3 Conversion** (if `--mp3`)
- Uses FFmpeg to convert WAV to MP3
- Default: 320kbps VBR (quality 0)
- Saves to `exports/audio/`
- Fallback to LAME if FFmpeg not available

### **Step 7: Video Creation** (if `--video`)
- Uses FFmpeg to create waveform visualization
- Resolution: 1280x720 (HD)
- Frame rate: 30 fps
- Includes title and artist overlay
- Zoom/pan effect on waveform
- Saves to `exports/video/`

### **Step 8: YouTube Upload** (if `--youtube`)
- Uses `youtube-upload` CLI tool
- Configures metadata (title, description, tags)
- Sets privacy (public by default)
- Uploads video and returns URL
- Fallback to manual upload instructions

---

## 📁 **FILE STRUCTURE**

The pipeline creates and uses these directories:

```
ableton-mcp-extended/
├── exports/
│   ├── audio/            # WAV and MP3 files
│   │   ├── MixName_YYYYMMDD_HHMMSS.wav
│   │   └── MixName_YYYYMMDD_HHMMSS.mp3
│   │
│   └── video/            # MP4 videos
│       └── MixName_YYYYMMDD_HHMMSS.mp4
│
└── scripts/
    ├── production_pipeline.py  # Main pipeline
    ├── polish_suite.py          # Polish tools
    ├── mix_master.py            # Mix generators
    └── ...                      # Other generators
```

---

## 🎯 **DUB TECHNO EXAMPLE**

Let's break down what happens with:
```bash
python scripts/production_pipeline.py dub_techno --mp3 --title "Dub Techno Mix"
```

### **Project Structure**

**9 Sections** (272 bars total, ~11 minutes at 125 BPM):

| # | Bars | Section | Scene | BPM | Energy |
|---|------|---------|-------|-----|--------|
| 1 | 0-31 | Dub Space Intro | 0 | 125 | 2/10 |
| 2 | 32-63 | Dub Steppers | 1 | 125 | 5/10 |
| 3 | 64-79 | Echo Build | 2 | 125 | 7/10 |
| 4 | 80-111 | Dub Bomb | 3 | 125 | 9/10 |
| 5 | 112-143 | Deep Dub Bass | 1 | 125 | 6/10 |
| 6 | 144-175 | Atmospheric Break | 4 | 125 | 3/10 |
| 7 | 176-191 | Reverb Rise | 2 | 125 | 8/10 |
| 8 | 192-239 | Filter Sweep Drop | 3 | 125 | 9.5/10 |
| 9 | 240-271 | Dub Techno Outro | 0 | 125 | 2/10 |

### **Track Configuration**

| # | Name | Type | Volume | Pan |
|---|------|------|--------|-----|
| 0 | Sub Bass (Dub) | bass | -4.0dB | 0.0 |
| 1 | Kick (Techno) | drum | -2.0dB | 0.0 |
| 2 | Snare/Clap | drum | -5.0dB | +0.15 |
| 3 | Hi-Hats | drum | -8.0dB | -0.15 |
| 4 | Atmospheric Pads | melody | -12.0dB | +0.3 |
| 5 | Dub Echo FX | fx | -15.0dB | +0.5 |
| 6 | Filter Sweep | fx | -12.0dB | 0.0 |
| 7 | White Noise | fx | -18.0dB | 0.0 |

### **What to Do in Ableton**

After the pipeline sets up the structure:

1. **Scene 0 (Intro/Outro)**:
   - Sub bass (sustained, filtered low)
   - Atmospheric pad (long reverb)
   - Filter sweep base (slow automation)

2. **Scene 1 (Main Groove)**:
   - Sub bass (steppers pattern)
   - Techno kick (4/4)
   - Snare on 2 & 4
   - Closed hi-hats (16th)
   - Atmospheric pad (subtle)
   - Echo FX (subtle)

3. **Scene 2 (Build)**:
   - Kick (every beat, getting louder)
   - Filter sweep up (2-octave rise)
   - White noise rise
   - Echo feedback increasing

4. **Scene 3 (Drop)**:
   - Sub bass (full, no filter)
   - Techno kick (full volume)
   - Snare on 2 & 4
   - Hi-hats (16th)
   - Atmospheric pad (full)
   - Echo maximum
   - Filter sweep in motion

5. **Scene 4 (Breakdown)**:
   - Atmospheric pad (full)
   - Dub echo delay (creating space)
   - Filter sweep subtle

---

## 🔧 **CUSTOMIZATION**

### **Create Your Own Genre**

Edit `production_pipeline.py` and add your genre configuration:

```python
"my_genre": {
    "name": "My Genre",
    "bpm": 130,
    "sections": [
        {"name": "Intro", "type": "intro", "bars": 16, "energy": 0.2, "scene": 0},
        {"name": "Verse", "type": "verse", "bars": 16, "energy": 0.5, "scene": 1},
        # ... more sections
    ],
    "tracks": [
        {"name": "Kick", "type": "drum", "volume": -3.0, "pan": 0.0},
        {"name": "Bass", "type": "bass", "volume": -5.0, "pan": 0.0},
        # ... more tracks
    ]
}
```

Then use it:
```bash
python scripts/production_pipeline.py custom --genre my_genre --bpm 130 --mp3
```

---

## 🎚️ **AUDIO SETTINGS**

The pipeline uses these default settings:

### **WAV Export**
- Format: WAV (uncompressed)
- Bit Depth: 24-bit
- Sample Rate: 44100 Hz
- Normalize: OFF (already balanced by polish suite)

### **MP3 Conversion**
- Codec: libmp3lame (FFmpeg)
- Quality: 0 (highest VBR quality)
- Bitrate: ~240 kbps average
- Fallback: LAME encoder

### **Customizing Audio Settings**

Edit `production_pipeline.py`:

```python
AUDIO_SETTINGS = {
    "format": "wav",
    "bit_depth": 24,        # or 16
    "sample_rate": 44100,   # or 48000
    "normalize": False,
    "mp3_bitrate": "320k",  # or "192k", "256k"
    "mp3_quality": 0        # 0-9, 0=highest
}
```

---

## 📹 **VIDEO SETTINGS**

The pipeline creates **waveform visualization videos** with:

### **Default Settings**
- Resolution: 1280x720 (HD)
- Frame Rate: 30 fps
-Duration: Matches audio length
- Colors: Red, teal, blue, yellow (waveform)
- Background: Dark blue (#1a1a2e)
- Title: White, 48pt, centered
- Artist: White, 24pt, centered bottom
- Effect: Zoom/pan on waveform

### **Customizing Video Settings**

Edit `production_pipeline.py`:

```python
VIDEO_SETTINGS = {
    "resolution": "1280x720",  # or "1920x1080", "640x360"
    "fps": 30,                   # or 24, 60
    "waveform_colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFBE0B"],
    "background_color": "#1a1a2e",
    "background_image": None,   # or "path/to/image.jpg"
    "title_font": "Arial Bold",
    "title_color": "#FFFFFF",
    "title_size": 48
}
```

---

## 📺 **YOUTUBE SETTINGS**

### **API Configuration**

Create `youtube_client_secrets.json`:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost:8080"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

### **Customizing YouTube Settings**

Edit `production_pipeline.py`:

```python
YOUTUBE_API_CONFIG = {
    "enabled": True,                 # or False
    "client_secrets_file": "youtube_client_secrets.json",
    "scope": ["https://www.googleapis.com/auth/youtube.upload"],
    "privacy_status": "public"       # or "private", "unlisted"
}
```

### **Manual Upload**

If you don't have API access, the pipeline will guide you through manual upload:

1. Go to YouTube Studio
2. Upload the video file
3. Fill in the metadata
4. Copy the URL and paste it

---

## 🔄 **WORKFLOW RECOMMENDATIONS**

### **For Quick Mixes**
```bash
# Just create structure, no export
python scripts/production_pipeline.py dub_techno
```
**Time**: ~5 seconds
**Use case**: Testing, practicing, live performance setup

---

### **For Production Mixes**
```bash
# Create, polish, export to MP3
python scripts/production_pipeline.py dub_techno --mp3
```
**Time**: ~10 seconds (plus manual WAV export)
**Use case**: Studio production, sharing with others

---

### **For Social Media**
```bash
# Create, polish, MP3, video
python scripts/production_pipeline.py techno --mp3 --video \
    --title "My Techno Mix" --artist "My Name"
```
**Time**: ~15-30 seconds (plus manual WAV export and video creation)
**Use case**: Instagram, TikTok, YouTube Shorts

---

### **For YouTube Upload**
```bash
# Complete workflow
python scripts/production_pipeline.py dub_techno --mp3 --video --youtube \
    --title "Dub Techno Mix - July 2026" \
    --artist "DJ Name" \
    --description "Generated with Ableton MCP Extended"
```
**Time**: ~1-2 minutes (plus upload time)
**Use case**: Publishing complete mixes to YouTube

---

### **For Live Performance**
```bash
# Setup with capture for live recording
python scripts/production_pipeline.py techno --capture
```
**Use case**: Record your live session to arrangement view

---

## 🐛 **TROUBLESHOOTING**

### **FFmpeg Not Found**

**Error**: `ffmpeg: command not found`

**Solution**:
- Download and install FFmpeg from https://ffmpeg.org/
- Add to PATH
- Verify installation: `ffmpeg -version`

---

### **LAME Not Found**

**Error**: `lame: command not found`

**Solution**:
- Install LAME: `brew install lame` (Mac) or `sudo apt install lame` (Linux)
- Or use FFmpeg only (preferred)

---

### **Connection Failed**

**Error**: `Failed to connect to Ableton Remote Script`

**Solution**:
- Make sure Ableton is running
- Verify Remote Script is installed
- Check port (default: 9877)
- Restart MCP Server: `python -m MCP_Server.server`

---

### **YouTube Upload Failed**

**Error**: `youtube-upload: command not found`

**Solution**:
- Install: `pip install youtube-upload`
- Or set up Google API credentials
- Or use manual upload (fallback)

---

### **Video Creation Failed**

**Error**: `Video creation failed: <error message>`

**Solution**:
- Check FFmpeg is installed and working
- Verify video settings are valid
- Use `--no-video` to skip video creation
- Manual video creation is always an option

---

## 📚 **RELATED DOCUMENTATION**

- **[MASTER_CONTROL.md](MASTER_CONTROL.md)** - Complete workflow guide
- **[COMPLETE_SYSTEM_SUMMARY.md](COMPLETE_SYSTEM_SUMMARY.md)** - Full system overview
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Quick reference
- **[INDEX.md](INDEX.md)** - Navigation to all docs

---

## 🎯 **BEST PRACTICES**

### **Before Starting**
1. ✅ **Backup your Ableton set**
2. ✅ **Test connection** with `scripts/test_connection_now.py`
3. ✅ **Have FFmpeg installed** for audio/video processing
4. ✅ **Configure your scenes** with appropriate clips
5. ✅ **Arm your tracks** for capture mode

### **During Production**
1. ✅ **Follow the locators** when triggering scenes manually
2. ✅ **Check levels** don't clip (master at -6dB or lower)
3. ✅ **Test transitions** between scenes
4. ✅ **Save your set** frequently
5. ✅ **Export with headroom** (no normalization)

### **After Production**
1. ✅ **Verify MP3 quality** (play and compare with WAV)
2. ✅ **Check video sync** (waveform matches audio)
3. ✅ **Review YouTube metadata** before publishing
4. ✅ **Backup your files** (WAV, MP3, video, project JSON)
5. ✅ **Document your settings** for future reference

---

## 🏁 **CONCLUSION**

The **Production Pipeline** provides a **complete, professional-grade** workflow for:

1. **Mix Creation** - Any genre, any BPM, any structure
2. **Ableton Integration** - Seamless setup with your DAW
3. **Audio Export** - WAV to MP3 conversion
4. **Video Creation** - Waveform visualization
5. **Distribution** - YouTube upload with metadata

**Everything is automated, yet you maintain complete creative control.**

---

## 🚀 **QUICK COMMAND REFERENCE**

```
┌─────────────────────────────────────────────────────────────┐
│              PRODUCTION PIPELINE CHEAT SHEET                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BASIC:                                                       │
│    python production_pipeline.py dub_techno                  │
│    python production_pipeline.py techno --mp3                │
│                                                             │
│  WITH EXPORT:                                                │
│    python production_pipeline.py dub_techno --mp3            │
│    python production_pipeline.py house --mp3 --title "Mix"  │
│                                                             │
│  WITH VIDEO:                                                 │
│    python production_pipeline.py dub_techno --mp3 --video   │
│    python production_pipeline.py techno --video --title T   │
│                                                             │
│  FULL WORKFLOW:                                              │
│    python production_pipeline.py dub_techno --mp3 --video   │
│      --youtube --title "Dub Techno" --artist "Me"           │
│                                                             │
│  CUSTOM:                                                     │
│    python production_pipeline.py custom --genre hiphop       │
│      --bpm 90 --mp3 --title "My Hip-Hop Mix"                │
│                                                             │
│  HELP:                                                       │
│    python production_pipeline.py --help                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎉 **READY TO CREATE?**

**Start with this command:**
```bash
python scripts/production_pipeline.py dub_techno --mp3 --title "My First Dub Techno Mix"
```

**The pipeline will guide you through the rest!**

---

**Version**: 1.0  
**Status**: PRODUCTION READY ✅  
**Last Updated**: July 2026  

---

**Happy producing!** 🎶✨
