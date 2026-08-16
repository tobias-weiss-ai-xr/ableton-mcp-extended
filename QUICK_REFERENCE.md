# Production Pipeline - Quick Reference

> **FAST TRACK: From Idea to Finished Mix in Minutes**

---

## ⚡ **30-SECOND START**

```bash
# Create Dub Techno mix
python scripts/production_pipeline.py dub_techno --mp3
```

That's it! The pipeline will:
1. ✅ Setup Ableton structure
2. ✅ Configure tracks and volumes
3. ✅ Polish the mix
4. ✅ Guide you through WAV export
5. ✅ Convert to MP3 automatically

---

## 📋 **COMMAND CHEAT SHEET**

### **Mix Creation**

| What You Want | Command |
|---------------|---------|
| Basic setup | `python production_pipeline.py dub_techno` |
| Setup + MP3 | `python production_pipeline.py dub_techno --mp3` |
| With custom title | `python production_pipeline.py techno --mp3 --title "My Mix"` |
| With custom BPM | `python production_pipeline.py dub --mp3 --bpm 75` |
| Custom genre | `python production_pipeline.py custom --genre hiphop --bpm 90 --mp3` |

### **Video Creation**

| What You Want | Command |
|---------------|---------|
| Basic video | `python production_pipeline.py dub_techno --mp3 --video` |
| Video with title | `python production_pipeline.py techno --mp3 --video --title "Techno Mix"` |

### **YouTube Upload**

| What You Want | Command |
|---------------|---------|
| Full workflow | `python production_pipeline.py dub_techo --mp3 --video --youtube` |
| With metadata | `python production_pipeline.py techno --mp3 --video --youtube --title "Mix" --artist "Name"` |

---

## 🎯 **GENRE LIST**

| Mix Type | Genre | BPM | Duration | Command |
|----------|-------|-----|----------|---------|
| `dub_techno` | Dub Techno | 125 | ~11 min | `py ... dub_techno` |
| `dub` | Dub | 75 | ~22 min | `py ... dub` |
| `techno` | Techno | 128 | ~11 min | `py ... techno` |
| `hiphop` | Hip-Hop | 85 | ~10 min | `py ... hiphop` |
| `house` | House | 120 | ~9 min | `py ... house` |
| `dnb` | Drum & Bass | 174 | ~8 min | `py ... dnb` |
| `ambient` | Ambient | 60 | ~43 min | `py ... ambient` |
| `custom` | Custom | Any | Variable | `py ... custom --genre X --bpm Y` |

---

## 🔧 **KEY FLAGS**

| Flag | Description | Example |
|------|-------------|---------|
| `--mp3` | Convert to MP3 | `--mp3` |
| `--video` | Create waveform video | `--video` |
| `--youtube` | Upload to YouTube | `--youtube` |
| `--capture` | Manual scene capture | `--capture` |
| `--no-polish` | Skip polish pass | `--no-polish` |
| `--dry-run` | Preview only | `--dry-run` |
| `--title` | Custom title | `--title "My Mix"` |
| `--artist` | Artist name | `--artist "My Name"` |
| `--bpm` | Custom BPM | `--bpm 120` |
| `--genre` | Custom genre | `--genre house` |

---

## 🎛️ **DUB TECHNO IN DETAIL**

### **Structure (272 bars / ~11 min)**

| Bar | Section | Scene | BPM | Energy | Description |
|-----|---------|-------|-----|---------|-------------|
| 0-31 | Dub Space Intro | 0 | 125 | 20% | Echoes, filter sweeps rising |
| 32-63 | Dub Steppers | 1 | 125 | 50% | 4/4 kick meets dub bassline |
| 64-79 | Echo Build | 2 | 125 | 70% | Echo feedback increasing |
| 80-111 | Dub Bomb | 3 | 125 | 90% | Full dub effects+techno energy |
| 112-143 | Deep Dub Bass | 1 | 125 | 60% | Sub 60Hz bass+subtle kicks |
| 144-175 | Atmospheric Break | 4 | 125 | 30% | Echo chambers+pads |
| 176-191 | Reverb Rise | 2 | 125 | 80% | Reverb tails growing |
| 192-239 | Filter Sweep Drop | 3 | 125 | 95% | Filter siren+pounding kick |
| 240-271 | Dub Techno Outro | 0 | 125 | 20% | Slow fade with dub echo decay |

### **Track Setup**

| # | Name | Volume | Pan | Purpose |
|---|------|--------|-----|---------|
| 0 | Sub Bass (Dub) | -4dB | 0.0 | Deep dub bass |
| 1 | Kick (Techno) | -2dB | 0.0 | 4/4 kick |
| 2 | Snare/Clap | -5dB | +0.15 | Snare on 2&4 |
| 3 | Hi-Hats | -8dB | -0.15 | 16th hats |
| 4 | Atmospheric Pads | -12dB | +0.3 | Atmosphere |
| 5 | Dub Echo FX | -15dB | +0.5 | Echo/delay |
| 6 | Filter Sweep | -12dB | 0.0 | Auto filter |
| 7 | White Noise | -18dB | 0.0 | Risers |

### **Scene Configuration**

| Scene | Name | Contents |
|-------|------|----------|
| 0 | Intro/Outro | Atmosphere, Dub Echo, Filter Base |
| 1 | Main Groove | Sub Bass, Kick, Snare, Hi-Hats, Pads |
| 2 | Build | Filter Sweep Up, White Noise Rise, Echo |
| 3 | Drop | Full Kick, Sub Bass, Atmosphere, Echo Max |
| 4 | Breakdown | Atmosphere Only, Dub Echo Delay |

---

## 📂 **OUTPUT FILES**

After the pipeline completes, files are saved to:

```
exports/
├── audio/
│   ├── Dub_Techno_YYYYMMDD_HHMMSS.wav    # WAV (manual export)
│   └── Dub_Techno_YYYYMMDD_HHMMSS.mp3    # MP3 (auto converted)
│
└── video/
    └── Dub_Techno_YYYYMMDD_HHMMSS.mp4    # Video (if --video)
```

---

## 🚀 **WORKFLOW EXAMPLES**

### **Example 1: Quick Demo (30 seconds)**

```bash
python scripts/production_pipeline.py dub_techno
```

**Use case**: Live performance prep, testing

**Outputs**: Ableton structure only (no export)

---

### **Example 2: Social Media Ready (~2 minutes)**

```bash
python scripts/production_pipeline.py techno --mp3 --video \
    --title "My Techno Mix" --artist "My DJ Name"
```

**Use case**: Instagram, TikTok, YouTube Shorts

**Outputs**: MP3 + waveform video

---

### **Example 3: Full YouTube Upload (~5 minutes)**

```bash
python scripts/production_pipeline.py dub_techno --mp3 --video --youtube \
    --title "Dub Techno Mix - July 2026" \
    --artist "My DJ Name" \
    --description "Fresh dub techno from the studio"
```

**Use case**: Publishing to YouTube

**Outputs**: MP3 + video + YouTube URL

---

## ⚙️ **SETTINGS**

### **Audio Quality**

| Setting | Default | Customize in `production_pipeline.py` |
|---------|---------|-------------------------------------|
| Bit Depth | 24-bit | `AUDIO_SETTINGS['bit_depth']` |
| Sample Rate | 44100 Hz | `AUDIO_SETTINGS['sample_rate']` |
| MP3 Quality | Highest VBR | `AUDIO_SETTINGS['mp3_quality']` |

### **Video Quality**

| Setting | Default | Customize in `production_pipeline.py` |
|---------|---------|-------------------------------------|
| Resolution | 1280x720 (HD) | `VIDEO_SETTINGS['resolution']` |
| Frame Rate | 30 fps | `VIDEO_SETTINGS['fps']` |
| Waveform Colors | Red/Teal/Blue/Yellow | `VIDEO_SETTINGS['waveform_colors']` |

### **YouTube Settings**

| Setting | Default | Customize in `production_pipeline.py` |
|---------|---------|-------------------------------------|
| Privacy | Public | `YOUTUBE_API_CONFIG['privacy_status']` |

---

## 🐛 **TROUBLESHOOTING**

### **"Connection failed"**

1. Start Ableton Live
2. Enable Remote Script in Preferences
3. Restart MCP Server: `python -m MCP_Server.server`

### **"FFmpeg not found"**

1. Download FFmpeg: https://ffmpeg.org/
2. Extract and add to PATH
3. Verify: `ffmpeg -version`

### **"Manual WAV export required"**

This is **normal**! The pipeline guides you through exporting from Ableton.

1. Open Ableton
2. File → Export Audio/Video...
3. Follow the pipeline's settings
4. Save to the specified location
5. Press Enter in the pipeline to continue

### **"YouTube upload failed"**

1. Install: `pip install youtube-upload`
2. Configure Google API credentials
3. Or use manual upload (pipeline will guide you)

---

## 📚 **DOCUMENTATION**

| Document | Description |
|----------|-------------|
| `[PIPELINEREADME.md](PIPELINEREADME.md)` | Complete workflow guide |
| `[MASTER_CONTROL.md](MASTER_CONTROL.md)` | Full system control |
| `[COMPLETE_SYSTEM_SUMMARY.md](COMPLETE_SYSTEM_SUMMARY.md)` | System overview |
| `[FINAL_SUMMARY.md](FINAL_SUMMARY.md)` | Quick reference |

---

## 🎯 **BEST PRACTICES**

✅ **Save your Ableton set before running**
✅ **Check connection with `test_connection_now.py`**
✅ **Test with `--dry-run` first**
✅ **Export with headroom (no clipping)**
✅ **Verify MP3 quality (play it!)**
✅ **Backup your files**

❌ **Don't skip polish unless you know what you're doing**
❌ **Don't normalize the WAV export**
❌ **Don't use lowest MP3 quality**
❌ **Don't forget to arm tracks for capture mode**

---

## 🚀 **READY TO CREATE?**

Start here:
```bash
python scripts/production_pipeline.py dub_techno --mp3 --title "My First Mix"
```

The pipeline does the rest!

---

**Command to get help:**
```bash
python scripts/production_pipeline.py --help
```

---

**Version**: 1.0  
**Status**: PRODUCTION READY ✅
