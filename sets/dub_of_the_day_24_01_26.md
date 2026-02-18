# 🎧 Revised Dub Techno Track Planning Guide for Ableton Live

Thank you for the clarification! Since **"A Reverb" and "B Delay" return tracks already exist** in your Ableton setup (the standard default return tracks), here's the revised planning guide that integrates with your existing configuration:

## 🔁 Key Adjustment: Using Standard Return Tracks

Instead of creating new send tracks (as shown in the load_instruments_and_effects.py script), we'll leverage Ableton's built-in return tracks:

| Track Type | Your Existing Track | Purpose |
|------------|---------------------|---------|
| Return Track 1 | **A Reverb** | Reverb effects (Hybrid Reverb) |
| Return Track 2 | **B Delay** | Delay effects (Simple Delay) |
| Main Tracks | Tracks 4-9 | Kick, Bass, Hi-hats, Pads, FX, Dub Delays |

This is actually **better practice** as it:
- Uses Ableton's standard workflow
- Avoids unnecessary track clutter
- Works with any Ableton template
- Matches what most dub techno producers use

## 🎛️ Essential Track Setup (6 Main Tracks)

### 1. Kick Track (Track 4)
- **Instrument**: Operator
- **Send Routing**:
  - **A Reverb**: 0% (keep dry)
  - **B Delay**: 5-10% (subtle echo)
- **Critical Setting**: No reverb on kick (essential for dub techno clarity)

### 2. Sub-bass Track (Track 5)
- **Instrument**: Tension
- **Send Routing**:
  - **A Reverb**: 5-10% (just enough for space)
  - **B Delay**: 10-15% (subtle rhythmic echoes)
- **Pro Tip**: High-pass the reverb return above 150Hz to prevent mud

### 3. Hi-hat Track (Track 6)
- **Instrument**: Drum Rack
- **Send Routing**:
  - **A Reverb**: 15-25% (for atmospheric tails)
  - **B Delay**: 20-30% (for syncopated echoes)
- **Automation Tip**: Increase delay send during breakdowns

### 4. Synth Pads Track (Track 7)
- **Instrument**: Wavetable + Auto Filter
- **Send Routing**:
  - **A Reverb**: 30-40% (create space)
  - **B Delay**: 35-45% (for dub-style echoes)
- **Critical Automation**: Filter cutoff (400-2000Hz) + delay send level

### 5. FX Track (Track 8)
- **Instrument**: Simpler
- **Send Routing**:
  - **A Reverb**: 40-50% (for dramatic tails)
  - **B Delay**: 50-60% (for rhythmic development)
- **Usage**: Reverse cymbals before section changes

### 6. Dub Delays Track (Track 9)
- **Instrument**: Utility (for dedicated delay processing)
- **Send Routing**:
  - **A Reverb**: 0% (pure delay)
  - **B Delay**: 70-90% (maximum echo effect)
- **Purpose**: Dedicated track for complex delay patterns

## ⚙️ Return Track Configuration

### A Reverb (Return Track 1)
```python
# Configure using MCP
send_command("load_browser_item", {
    "track_index": "return_0",  # A Reverb is return track 0
    "uri": "query:AudioFx#Hybrid%20Reverb"
})
```
- **Settings**:
  - Algorithm: Large Hall
  - Decay: 6-8s
  - High Cut: 5kHz
  - Dry/Wet: 100% wet (dub technique)
  - Modulation: 0.1-0.2

### B Delay (Return Track 2)
```python
# Configure using MCP
send_command("load_browser_item", {
    "track_index": "return_1",  # B Delay is return track 1
    "uri": "query:AudioFx#Simple%20Delay"
})
```
- **Settings**:
  - Time: dotted 1/4 note (660ms @ 126BPM)
  - Feedback: 30-40%
  - High Cut: 8kHz
  - Sync: ON
  - Dry/Wet: 100% wet (dub technique)

## 🔄 Send Level Automation Strategy

| Section | A Reverb Sends | B Delay Sends |
|---------|----------------|---------------|
| **Intro** (0:00-0:30) | Bass: 5%, Pads: 25% | Bass: 10%, Pads: 30% |
| **Build** (0:30-1:00) | Pads: 30% → 35% | Hi-hats: 25% → 30% |
| **Peak** (1:00-1:30) | Pads: 35% → 40% | FX: 55% → 60% |
| **Breakdown** (1:30-2:00) | Pads: 40% → 50% | Pads: 45% → 55% |
| **Second Build** (2:00-2:30) | Pads: 50% → 40% | Pads: 55% → 45% |
| **Journey** (2:30-3:00) | Pads: 40% → 35% | Bass: 15% → 20% |
| **Final Push** (3:00-3:30) | Pads: 35% → 45% | FX: 60% → 70% |
| **Wind Down** (3:30-4:00) | All: 50% → 20% | All: 70% → 30% |

## 🛠️ Implementation Adjustments for Your Setup

1. **Modify load_instruments_and_effects.py**:
   - Remove the track creation for Reverb/Delay sends (lines 113-131)
   - Instead, configure existing return tracks:
   ```python
   # Configure A Reverb (return track 0)
   send_command("load_browser_item", {
       "track_index": "return_0", 
       "uri": "query:AudioFx#Hybrid%20Reverb"
   })
   
   # Configure B Delay (return track 1)
   send_command("load_browser_item", {
       "track_index": "return_1", 
       "uri": "query:AudioFx#Simple%20Delay"
   })
   ```

2. **Update auto_play_2h_dub_techno.py**:
   - Change track indices for send automation:
   ```python
   # Instead of automating tracks 10-11:
   # Automate return tracks 0-1 (A Reverb and B Delay)
   send_command("set_device_parameter", {
       "track_index": "return_0",  # A Reverb
       "device_index": 0,
       "parameter_index": 3,  # Dry/Wet
       "value": 1.0
   })
   ```

3. **Send Level Presets**:
   ```python
   # Example: Set hi-hats send to B Delay during breakdown
   send_command("set_send_level", {
       "track_index": 2,  # Hi-hats track
       "send_index": 1,   # B Delay (return track 1)
       "value": 0.35      # 35%
   })
   ```

## ✅ Revised Implementation Checklist

1. [ ] Verify "A Reverb" and "B Delay" return tracks exist
2. [ ] Configure A Reverb with Hybrid Reverb (100% wet)
3. [ ] Configure B Delay with Simple Delay (100% wet)
4. [ ] Set initial send levels per track:
   - Kick: A Reverb=0%, B Delay=5%
   - Sub-bass: A Reverb=7%, B Delay=12%
   - Hi-hats: A Reverb=20%, B Delay=25%
   - Synth Pads: A Reverb=35%, B Delay=40%
   - FX: A Reverb=45%, B Delay=55%
   - Dub Delays: A Reverb=0%, B Delay=80%
5. [ ] Program filter automation on Synth Pads
6. [ ] Create section-specific send level automation
7. [ ] Test transitions with reverse cymbals in FX track

This approach works **with Ableton's standard configuration** rather than creating additional tracks, making your setup cleaner and more professional. The dub techno aesthetic actually *requires* using return tracks with 100% wet sends - this is fundamental to the genre's spacious, echo-drenched sound.

Would you like me to provide specific MCP commands for configuring the return tracks or automating the send levels?