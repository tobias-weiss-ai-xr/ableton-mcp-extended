# 10-Minute Dub Reggae - Testing Guide

## Pre-Flight Checks

### 1. Syntax Verification
```bash
# Check Python syntax
python -m py_compile create_10min_dub_reggae.py
python -m py_compile play_10min_dub_reggae.py

# Expected: No output (means syntax is valid)
```
**Status:** ✅ PASS - Both scripts compile without errors

---

## Test Environment Setup

### Required Components

1. **Ableton Live 11+** installed and running
2. **AbletonMCP Remote Script** loaded:
   - Copy `AbletonMCP_Remote_Script/` to:
     - Windows: `C:\Users\[User]\Documents\Ableton\User Library\Remote Scripts\`
     - Mac: `~/Music/Ableton/User Library/Remote Scripts/`
   - Enable in Ableton: Preferences → Link MIDI → C:Users
3. **MCP Server** running:
   ```bash
   cd MCP_Server
   python server.py
   ```
   - Should see: "AbletonMCP server starting up"
   - Should see: "Successfully connected to Ableton"

### Verify Connectivity

```bash
# Test MCP server connection
cd MCP_Server
python -c "
import socket
import json
s = socket.socket()
try:
    s.connect(('localhost', 9877))
    print('✅ Connected to Ableton MCP server on port 9877')
    s.send(json.dumps({'type': 'get_session_info', 'params': {}}).encode('utf-8'))
    response = json.loads(s.recv(8192).decode('utf-8'))
    print(f'✅ Ableton responding - Session info received')
    s.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

---

## Manual Testing Procedure

### Test 1: Track Creation (`create_10min_dub_reggae.py`)

**Setup:**
1. Open Ableton Live
2. Create new empty set
3. Verify Remote Script is loaded (check Preferences → Link MIDI)
4. Start MCP Server in terminal
5. Run creation script:
   ```bash
   python create_10min_dub_reggae.py
   ```

**Expected Output:**
```
================================================================================
CREATING 10-MINUTE DUB REGGAE BEAT
================================================================================
Tempo: 75 BPM (classic dub tempo)
Duration: 10 minutes
Structure: 10 sections x 1 minute each
================================================================================

Setting tempo to 75 BPM...
   [OK] Tempo set to 75 BPM

================================================================================
STEP 1: CREATING TRACKS
================================================================================
   [OK] Created Kick at Track 4
   [OK] Created Snare at Track 5
   [OK] Created Hi-hats at Track 6
   [OK] Created Dub Bass at Track 7
   [OK] Created Guitar Chop at Track 8
   [OK] Created Organ Bubble at Track 9
   [OK] Created FX at Track 10
   [OK] Created Reverb Send at Track 11
   [OK] Created Delay Send at Track 12

Track indices: {...}
...

================================================================================
STEP 2: CREATING DRUM CLIPS
================================================================================

Creating 4 Kick clips...
   [OK] Created Kick clip 0: Kick One Drop
   [OK] Created Kick clip 1: Kick Heavy
   [OK] Created Kick clip 2: Kick Light
   [OK] Created Kick clip 3: Kick Muted
...
```

**Verification in Ableton:**
- [ ] Tempo set to 75 BPM (top-left of Ableton interface)
- [ ] 10 new tracks created in Session View
- [ ] Tracks named correctly: Kick, Snare, Hi-hats, Dub Bass, Guitar Chop, Organ Bubble, FX, Dub Delays, Reverb Send, Delay Send
- [ ] Each track has clips in Session View slots:
  - Kick: 4 clips
  - Snare: 4 clips
  - Hi-hats: 4 clips
  - Dub Bass: 8 clips
  - Guitar Chop: 4 clips
  - Organ Bubble: 4 clips
  - FX: 4 clips
  - Dub Delays: 3 clips
- [ ] All clips are 4.0 beats long (1 bar)
- [ ] Clip names match expected patterns (e.g., "Kick One Drop", "Bass Root Drone C")

**Success Criteria:**
- ✅ All tracks created
- ✅ All clips created with correct notes
- ✅ No error messages in script output
- ✅ Tempo correctly set to 75 BPM

---

### Test 2: Manual Instrument Loading

**Setup Required:**
Scripts create tracks and clips but DO NOT load instruments. Manual setup needed:

1. **Kick Track:**
   - Load: Drum Rack (or Operator)
   - Preset: Kick drum
   - MIDI pitch 36 should produce kick sound

2. **Snare Track:**
   - Load: Drum Rack (or Simpler)
   - Preset: Snare drum
   - MIDI pitch 38 should produce snare sound

3. **Hi-hats Track:**
   - Load: Drum Rack (or Simpler)
   - Preset: Closed hi-hat (76), open hi-hat (77)
   - MIDI pitches 76-77 should produce hi-hat sounds

4. **Dub Bass Track:**
   - Load: Tension or Operator
   - Preset: Sub-bass or heavy bass
   - MIDI pitches 24-43 should produce deep bass notes

5. **Guitar Chop Track:**
   - Load: Instrument Rack or Simpler
   - Preset: Guitar or organ stabs
   - MIDI pitches 43-58 should produce chord sounds

6. **Organ Bubble Track:**
   - Load: Organ or Electric Piano
   - Preset: B3 organ or EP
   - MIDI pitches 55-63 should produce organ sounds

7. **FX Track:**
   - Load: Simpler or Drum Rack
   - Preset: Percussion samples
   - MIDI pitches 30-50 should produce FX sounds

8. **Dub Delays Track:**
   - Load: Utility (no audio input, for send routing)

9. **Reverb Send Track:**
   - Load: Reverb plugin
   - Settings: Large Hall, 2-3s decay, pre-delay 20-50ms

10. **Delay Send Track:**
    - Load: Simple Delay or Ping Pong Delay
    - Settings: 1/4 or 1/8 note, 35-50% feedback, low-pass filter 2-4 kHz

11. **Send Routing:**
    - For each of tracks 1-8 (Kick → FX):
      - Enable Send A → Delay Send (20-40%)
      - Enable Send B → Reverb Send (15-35%)

**Verification:**
- [ ] All 10 tracks have instruments/effects loaded
- [ ] Send tracks receive audio from other tracks
- [ ] MIDI notes produce correct sounds when clips play
- [ ] Send routing visible in Ableton mixer (send knobs show levels)

---

### Test 3: Clip Playback (Manual Test)

**Setup:**
1. Load instruments as per Test 2
2. Set up send routing as per Test 2
3. In Ableton Session View, manually trigger clips

**Procedure:**
1. Click Kick clip 0 ("Kick One Drop") - should hear kick on beat 3
2. Click Snare clip 0 ("Snare Basic") - should hear snare on beats 2 & 4
3. Click Hi-hats clip 0 ("Hi-hat Offbeat") - should hear offbeat hi-hats
4. Click Dub Bass clip 0 ("Bass Root Drone C") - should hear sustained C2 note
5. Click Guitar Chop clip 0 ("Chop C Major") - should hear offbeat C major triads
6. Click Organ Bubble clip 0 ("Organ Shuffle") - should hear double-time shuffle pattern

**Expected:**
- [ ] All clips play correct sounds
- [ ] Timing is accurate (at 75 BPM)
- [ ] One Drop pattern is authentic (kick on beat 3)
- [ ] Offbeat patterns sound correct (on "and" of beats)
- [ ] Bass is deep and prominent
- [ ] No timing issues or lag

---

### Test 4: Automation Playback (`play_10min_dub_reggae.py`)

**Setup:**
1. Complete Tests 1-3 (tracks, clips, instruments, sends loaded)
2. Start MCP Server if not running
3. Ensure Ableton Live is open with Remote Script loaded

**Procedure:**
```bash
python play_10min_dub_reggae.py
```

**Expected Output:**
```
================================================================================
10-MINUTE DUB REGGAE AUTOMATION
================================================================================
Tempo: 75 BPM
Duration: 10 minutes
Sections: 10 sections x 1 minute each
================================================================================

Finding tracks by name...
   [OK] Found Kick at Track 4
   [OK] Found Snare at Track 5
   [OK] Found Hi-hats at Track 6
   [OK] Found Dub Bass at Track 7
   [OK] Found Guitar Chop at Track 8
   [OK] Found Organ Bubble at Track 9
   [OK] Found FX at Track 10
   [OK] Found Dub Delays at Track 11

================================================================================
LOADING SECTIONS
================================================================================

Loaded 10 sections

================================================================================
STARTING AUTOMATED PLAYBACK
================================================================================

Press Ctrl+C to stop early

Starting playback...

[0] Intro: Minimal intro with bass and drums only
   Fire Kick clip 0
   Fire Snare clip 0
   Fire Hi-hats clip 0
   Fire Dub Bass clip 0
   Stop Guitar Chop
   Stop Organ Bubble
   Stop FX
   Stop Dub Delays

   Automation targets:
   - Filter frequency: 0.20 (manual adjustment required)
   - Reverb send: 0.30 (manual adjustment required)
   - Delay send: 0.20 (manual adjustment required)

   Progress: 10% (1/10 sections)
   Time: 1 min / 10 min
   Waiting 60 seconds...

[1] Build: Add guitar chop to the groove
   Fire Kick clip 0
   Fire Snare clip 0
   Fire Hi-hats clip 1
   Fire Dub Bass clip 4
   Fire Guitar Chop clip 0
   Stop Organ Bubble
   Stop FX
   Stop Dub Delays
...
```

**Verification in Ableton:**
- [ ] Playback starts automatically
- [ ] Clips fire in Session View (visible clip activation)
- [ ] Each section plays for approximately 60 seconds (15 bars at 75 BPM)
- [ ] Correct clips fire for each track per section
- [ ] Audio evolves through sections (intro → build → peak → breakdown)
- [ ] Progress displays in console
- [ ] Ctrl+C stops playback gracefully
- [ ] After 10 minutes, playback stops or continues as intended

**Success Criteria:**
- ✅ All 10 sections execute without errors
- ✅ Clips fire in correct sequence
- ✅ Musical journey matches arrangement (intro → peak → breakdown → rebuild)
- ✅ No connection errors to MCP server
- ✅ Progress updates display correctly
- ✅ Graceful shutdown on Ctrl+C

---

### Test 5: Manual Automation Verification

**Note:** Script logs automation targets but doesn't apply them automatically (would require device indices). Manual verification needed:

**Procedure:**
1. During automation playback, observe console output for automation targets
2. Manually adjust parameters in Ableton to match targets:

   **Filter Automation (on synth tracks):**
   - Section 0 (Intro): Set Auto Filter cutoff to 0.20 (~200 Hz)
   - Section 1 (Build): Increase to 0.30 (~400 Hz)
   - Section 3 (Peak 1): Increase to 0.70 (~800 Hz)
   - Section 4 (Breakdown): Decrease to 0.25 (~250 Hz)
   - Section 6 (Peak 2): Increase to 0.80 (~900 Hz)
   - Section 8 (Peak 3): Increase to 0.85 (~950 Hz)
   - Section 9 (Wind Down): Decrease to 0.20 (~200 Hz)

   **Send Level Automation:**
   - Reverb Send: Adjust between 0.30-0.80
   - Delay Send: Adjust between 0.20-0.60

**Expected Results:**
- [ ] Filter changes create sense of opening/closing
- [ ] Peaks sound brighter (filter open)
- [ ] Breakdowns sound muffled (filter closed)
- [ ] Reverb increases during breakdowns (space)
- [ ] Delay increases during peaks (echoes)

---

## Known Limitations

### 1. Manual Setup Required
- Scripts create tracks/clips but DO NOT load instruments
- Manual instrument loading required (as documented in Test 2)
- This is by design (MCP tools available don't include preset loading)

### 2. Manual Automation Required
- Script logs automation targets but doesn't apply them
- Manual parameter adjustment required (as documented in Test 5)
- Would require device indexing and parameter identification for full automation

### 3. Requires Ableton Live
- Cannot test scripts without Ableton Live running
- Cannot test without Remote Script loaded
- Cannot test without MCP Server running

### 4. Timing Depends on System
- 60 seconds per section depends on system timing
- May vary slightly based on CPU load
- Script assumes accurate system timing

---

## Troubleshooting

### Error: "Connection failed"

**Cause:** Ableton Live not running or MCP Server not started

**Solution:**
1. Open Ableton Live
2. Verify Remote Script is loaded (Preferences → Link MIDI)
3. Start MCP Server: `cd MCP_Server && python server.py`
4. Re-run script

### Error: "Track not found"

**Cause:** Tracks not created yet

**Solution:**
1. Run `create_10min_dub_reggae.py` first
2. Verify tracks appear in Ableton Session View
3. Re-run playback script

### Error: "No sound"

**Cause:** Instruments not loaded

**Solution:**
1. Load instruments on each track (see Test 2)
2. Load effects on send tracks
3. Set up send routing
4. Check track volumes

### Timing Issues

**Cause:** System lag or high CPU load

**Solution:**
1. Close other applications
2. Increase buffer size in Ableton
3. Monitor CPU usage in Ableton
4. Restart Ableton if issues persist

---

## Automated Test Script (Optional)

For basic connectivity testing without full Ableton setup:

```python
import socket
import json

def test_mcp_connection():
    """Test MCP server connectivity"""
    try:
        s = socket.socket()
        s.connect(('localhost', 9877))
        print("✅ Connected to MCP server on port 9877")

        # Test session info command
        s.send(json.dumps({'type': 'get_session_info', 'params': {}}).encode('utf-8'))
        response = json.loads(s.recv(8192).decode('utf-8'))
        print(f"✅ Session info: {response['result']['track_count']} tracks")

        # Test tempo setting
        s.send(json.dumps({'type': 'set_tempo', 'params': {'tempo': 75.0}}).encode('utf-8'))
        response = json.loads(s.recv(8192).decode('utf-8'))
        print(f"✅ Tempo set to 75 BPM")

        s.close()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_mcp_connection()
```

Run with:
```bash
python test_mcp_connection.py
```

---

## Final Verification Checklist

Before considering testing complete:

**Script Execution:**
- [ ] `create_10min_dub_reggae.py` runs without errors
- [ ] `play_10min_dub_reggae.py` runs without errors
- [ ] Both scripts compile without syntax errors
- [ ] Error handling works (Ctrl+C, connection failures)

**Ableton Integration:**
- [ ] Tracks created in Ableton Session View
- [ ] All clips created with correct notes
- [ ] Tempo set to 75 BPM
- [ ] Instruments load and produce correct sounds
- [ ] Send routing configured correctly

**Playback Functionality:**
- [ ] Automation script fires clips in sequence
- [ ] All 10 sections execute
- [ ] Progress displays correctly
- [ ] Musical journey matches arrangement
- [ ] Graceful shutdown works

**Dub Aesthetic:**
- [ ] One Drop pattern is authentic
- [ ] Offbeat rhythms sound correct
- [ ] Bass is prominent and deep
- [ ] Effects (reverb/delay) create dub atmosphere
- [ ] Overall 10-minute flow is cohesive

---

## Test Results

**Syntax Check:** ✅ PASS (both scripts compile)

**Ableton Integration:** ⏳ REQUIRES ABLETON LIVE (manual testing needed)

**Playback Automation:** ⏳ REQUIRES ABLETON LIVE (manual testing needed)

**Recommendation:** Run manual tests (Test 1-5) in Ableton Live environment to verify full functionality.
