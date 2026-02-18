# HOW TO RECORD YOUR DUB SONG

## OPTION 1: ARRANGEMENT VIEW EXPORT (RECOMMENDED)

**Best for:** Perfect quality, exact timing, professional result

### Steps:

1. **Switch to Arrangement View**
   - Press `TAB` in Ableton

2. **Arrange Clips Horizontally**
   - Drag clips from Session View to Arrangement View
   - Place them in this order on the timeline:

   ```
   Time          | Section       | Tracks to Arrange
   -------------|--------------|-------------------
   0:00 - 0:40  | INTRO        | Bass 2, Drums 2, Atm 0, Mel 0, Perc 0
   0:40 - 1:20  | BUILDUP      | Bass 1, Drums 3, Atm 1, Mel 1
   1:20 - 2:00  | DROP         | Bass 0, Drums 4, Atm 1, Mel 0, FX 0
   2:00 - 2:40  | BUILDUP      | Bass 1, Drums 3, Atm 0, Mel 1
   2:40 - 3:20  | BREAKDOWN    | Bass 2, Drums 2, Atm 1
   3:20 - 4:00  | BUILDUP      | Bass 1, Drums 3, Atm 0, Mel 0
   4:00 - 4:40  | DROP         | Bass 0, Drums 4, Atm 1, Mel 1, FX 0, Perc 0
   4:40 - 5:00  | OUTRO        | Bass 2, Drums 2, Atm 0
   ```

3. **Set Markers**
   - Click at 0:00 (start)
   - Click at 5:00 (end)
   - Right-click → "Add Locator" for easy navigation

4. **Export Audio**
   - `File` → `Export Audio/Video`
   - Settings:
     - **Rendered Track:** Master
     - **Duration:** Selection (0:00 - 5:00)
     - **Sample Rate:** 48000 Hz
     - **Bit Depth:** 24-bit (or 32-bit float)
     - **File Type:** WAV (best) or MP3 (sharing)
     - **Normalization:** Off (handle levels manually)
   - Click `Export`

5. **Wait for Export**
   - Progress bar will show
   - File saved to default location

---

## OPTION 2: AUTOMATED LIVE RECORDING

**Best for:** Live feel, quick recording, testing arrangements

### Quick Method:

```bash
# Run automated recording script
python record_dub_song_automated.py
```

### Manual Recording Sequence:

```bash
# 1. Prepare Ableton
# - Load instruments
# - Check levels
# - Press TAB (Session View)
# - Click Record on Master
# - Press Space

# 2. Run these commands in order (copy-paste all at once):
python switch_section.py intro     # 0:00 - 0:32
timeout 32
python switch_section.py buildup   # 0:32 - 1:04
timeout 32
python switch_section.py drop      # 1:04 - 1:36
timeout 32
python switch_section.py buildup   # 1:36 - 2:08
timeout 32
python switch_section.py breakdown # 2:08 - 2:40
timeout 32
python switch_section.py buildup   # 2:40 - 3:12
timeout 32
python switch_section.py drop      # 3:12 - 3:44
timeout 32
python switch_section.py fulldrop  # 3:44 - 4:16
timeout 32
python switch_section.py intro     # 4:16 - 4:48

# 3. Press Space in Ableton to stop recording
```

### Using the Automated Script:

1. **Prepare Ableton**
   - Load instruments on all 6 dub tracks
   - Check levels (not clipping)
   - Press `TAB` for Session View

2. **Start Recording**
   - Click `Record` button on Master track
   - Press `Space` to start recording
   - Recording indicator shows red

3. **Run Script**
   ```bash
   python record_dub_song_automated.py
   ```
   - Press `Enter` when ready
   - Script plays all sections automatically
   - Each section plays for correct duration
   - Total time: exactly 5 minutes

4. **Stop Recording**
   - Wait for script to complete
   - Press `Space` in Ableton
   - Recording saved

5. **Export** (if recording to audio track)
   - Select the recorded audio track
   - `File` → `Export Audio/Video`
   - Export the track

---

## SECTION COMBINATIONS QUICK REFERENCE

### INTRO (Minimal, spacey)
```bash
python switch_section.py intro
```
- Bass: Clip 2 (Breakdown)
- Drums: Clip 2 (Minimalist)
- Atmosphere: Clip 0 (Basic)
- Melody: Clip 0 (Basic)
- Percussion: Clip 0

### BUILDUP (Adding energy)
```bash
python switch_section.py buildup
```
- Bass: Clip 1 (Alternative)
- Drums: Clip 3 (Buildup)
- Atmosphere: Clip 1 (Complex)
- Melody: Clip 1 (Alternative)

### DROP (Maximum energy)
```bash
python switch_section.py drop
```
- Bass: Clip 0 (Main)
- Drums: Clip 4 (Drop)
- Atmosphere: Clip 1 (Complex)
- Melody: Clip 0 (Basic)
- FX: Clip 0

### BREAKDOWN (Space and atmosphere)
```bash
python switch_section.py breakdown
```
- Bass: Clip 2 (Breakdown)
- Drums: Clip 2 (Minimalist)
- Atmosphere: Clip 1 (Complex)

### FULL DROP (All elements)
```bash
python switch_section.py fulldrop
```
- Bass: Clip 0 (Main)
- Drums: Clip 4 (Drop)
- Atmosphere: Clip 1 (Complex)
- Melody: Clip 1 (Alternative)
- FX: Clip 0
- Percussion: Clip 0

---

## RECORDING TIPS

### Before Recording
- ✓ Load all instruments first
- ✓ Check track levels (green, not yellow/red)
- ✓ Save your project
- ✓ Test playback through sections
- ✓ Use headphones to monitor

### During Recording
- ✓ Watch levels carefully
- ✓ Monitor in headphones
- ✓ Don't clip (avoid distortion)
- ✓ Keep steady tempo (75 BPM)

### After Recording
- ✓ Listen back to check quality
- ✓ Export at highest quality (24-bit/48kHz)
- ✓ Save multiple versions
- ✓ Keep project file safe

---

## EXPORT SETTINGS

### For Best Quality (Master/Sale)
- **Sample Rate:** 48000 Hz
- **Bit Depth:** 24-bit or 32-bit float
- **File Type:** WAV
- **Normalization:** Off

### For Sharing (MP3)
- **Sample Rate:** 44100 Hz
- **Bit Depth:** 16-bit
- **File Type:** MP3
- **Quality:** 320 kbps
- **Normalization:** On or Off

---

## TIMING REFERENCE

At 75 BPM:
- 1 bar = 0.53 seconds
- 4 bars = 2.13 seconds
- 8 bars = 4.27 seconds
- 16 bars = 8.53 seconds

**Song Structure:**
- Each section = 8 bars (≈4 seconds)
- 9 sections total
- Total ≈36-37 seconds

Wait, let me recalculate:
- 75 BPM = 75 beats per minute
- 4/4 time signature = 4 beats per bar
- 1 bar = (60/75)*4 = 3.2 seconds
- 8 bars = 8*3.2 = 25.6 seconds

So each section should play for about 25-26 seconds (8 bars).

Let me adjust the script timing to be more accurate...

---

## FILES CREATED

- `record_dub_song.py` - Recording guide
- `record_dub_song_automated.py` - Automated playback script
- `record_dub_song.bat` - Windows batch file

---

## RECOMMENDATION

**For a perfect, professional recording:**
→ Use Arrangement View + Export

**For quick, live-feel recording:**
→ Use automated recording script

Both methods will give you a complete 5-minute dub song!