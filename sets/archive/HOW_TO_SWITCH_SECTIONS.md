# HOW TO SWITCH BETWEEN SECTIONS

## Option 1: Using the Section Switcher Script (Recommended)

I've created `section_switcher.py` that lets you switch sections with keyboard commands.

**To use it:**
1. Run: `python section_switcher.py`
2. Enter section numbers (1-5) to switch between sections
3. Press 'q' to quit

**Sections available:**
1. **INTRO** - Minimal, spacey dub atmosphere
2. **BUILDUP** - Adding energy and rhythm
3. **DROP** - Maximum energy with full groove
4. **BREAKDOWN** - Space and atmosphere, minimal elements
5. **FULL DROP** - All elements active

---

## Option 2: Using Ableton Session View (Manual)

### Session View Overview
In Ableton, Session View is where you launch clips and scenes.

### How to Switch Sections Manually:

#### Method A: Click on Individual Clips
1. Press **Tab** to switch to Session View (if in Arrangement View)
2. Click on any clip to fire it
3. Click on different clips to change the sound

**Clip Mapping:**
- **Track 4 (Dub Bass):** Clips 0-2
  - Clip 0: Main bass
  - Clip 1: Alternative bass
  - Clip 2: Breakdown bass

- **Track 5 (Drums):** Clips 2-4
  - Clip 2: Minimalist drums
  - Clip 3: Buildup drums
  - Clip 4: Drop drums

- **Track 6 (Atmosphere):** Clips 0-1
  - Clip 0: Basic atmosphere
  - Clip 1: Complex atmosphere

- **Track 7 (Dub Melody):** Clips 0-1
  - Clip 0: Basic melody
  - Clip 1: Alternative melody

- **Track 8 (FX):** Clip 0
  - Clip 0: FX sounds

- **Track 10 (Percussion):** Clip 0
  - Clip 0: Percussion

#### Method B: Use Scene Launch
1. In Session View, look at the **vertical columns** (scenes)
2. Click the **scene trigger** (the box at the far right of each row)
3. This launches all clips in that row simultaneously

**To create scenes for your sections:**
1. Select clips that form a section (e.g., for INTRO)
2. Press **Ctrl + Enter** (Windows) or **Cmd + Enter** (Mac)
3. This captures a scene with those clips
4. Name the scene by right-clicking and selecting "Rename"

---

## Option 3: Using Ableton Arrangement View

1. Press **Tab** to switch to Arrangement View
2. You'll see clips arranged horizontally across the timeline
3. Click the **Play button** to start from the beginning
4. The playback head moves automatically through the arrangement

**To arrange sections:**
1. Drag and drop clips from Session View to Arrangement View
2. Arrange them in order (Intro → Buildup → Drop → etc.)
3. Each section should be 8-16 bars (32-64 seconds)
4. Press **Space** to play/pause
5. Click anywhere in the timeline to jump to that point

---

## Quick Reference - Section Combinations

### INTRO Section:
- Track 4: Clip 2 (Breakdown Bass)
- Track 5: Clip 2 (Minimalist Drums)
- Track 6: Clip 0 (Basic Atmosphere)
- Track 7: Clip 0 (Basic Melody)
- Track 10: Clip 0 (Percussion)

### BUILDUP Section:
- Track 4: Clip 1 (Alternative Bass)
- Track 5: Clip 3 (Buildup Drums)
- Track 6: Clip 1 (Complex Atmosphere)
- Track 7: Clip 1 (Alternative Melody)

### DROP Section:
- Track 4: Clip 0 (Main Bass)
- Track 5: Clip 4 (Drop Drums)
- Track 6: Clip 1 (Complex Atmosphere)
- Track 7: Clip 0 (Basic Melody)
- Track 8: Clip 0 (FX)

### BREAKDOWN Section:
- Track 4: Clip 2 (Breakdown Bass)
- Track 5: Clip 2 (Minimalist Drums)
- Track 6: Clip 1 (Complex Atmosphere)

### FULL DROP Section:
- Track 4: Clip 0 (Main Bass)
- Track 5: Clip 4 (Drop Drums)
- Track 6: Clip 1 (Complex Atmosphere)
- Track 7: Clip 1 (Alternative Melody)
- Track 8: Clip 0 (FX)
- Track 10: Clip 0 (Percussion)

---

## Pro Tips

1. **Keyboard Shortcuts:**
   - **Tab**: Switch between Session/Arrangement View
   - **Space**: Play/Pause
   - **Enter**: Fire selected clip or scene
   - **L**: Toggle Launch quantization
   - **F**: Follow playback (in Arrangement View)

2. **MIDI Mapping:**
   - Map MIDI controllers to clips for live performance
   - Use MIDI keyboard to trigger sections
   - Settings → MIDI → Map to controls

3. **Automation:**
   - Add automation to clip volume/pan/effects
   - Create smooth transitions between sections
   - Use automation envelopes for filter sweeps

4. **Scene Launch Quantization:**
   - Set to "1 Bar" for smooth transitions
   - Settings → Record/Warp/Launch → Launch Quantization
   - This ensures clips start on the beat

---

## Troubleshooting

**Clips not playing?**
- Check track volume is up
- Make sure clips are not muted
- Check Master volume

**Sections not changing?**
- Make sure you're in Session View (Tab key)
- Click on clips directly
- Check Launch Quantization is not set to "None"

**Want to stop all clips?**
- Press the **Stop All Clips** button (square icon) in Session View
- Or press the **Space** bar twice

---

**RECOMMENDED:** Use `section_switcher.py` for easy switching during performance or to test different section combinations!